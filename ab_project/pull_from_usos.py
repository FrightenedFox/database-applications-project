import asyncio
import datetime as dt
import logging

import pytz

from ab_project.config.config import app_config
from ab_project.db import UsosDB
from ab_project.usosapi.usosapi import USOSAPIConnection

pl_tz = pytz.timezone("Europe/Warsaw")


def daterange(start_date: dt.date | dt.datetime, end_date: dt.date | dt.datetime, step: int = 1):
    for n in range(0, int((end_date - start_date).days), step):
        yield start_date + dt.timedelta(days=n)


async def pull_data(db: UsosDB):
    usos_connection = USOSAPIConnection(
        api_base_address=app_config.usosapi.api_base_address,
        consumer_key=app_config.usosapi.consumer_key,
        consumer_secret=app_config.usosapi.consumer_secret
    )

    print(usos_connection.get_authorization_url())
    usos_connection.authorize_with_pin(input("Enter pin code: "))
    logging.info(f"Authorization is successful: {usos_connection.is_authorized()}")

    user_info = usos_connection.current_identity()
    await asyncio.sleep(0.5)
    user_info["usos_id"] = user_info.pop("id")
    if not db.row_exists(key_value=user_info["usos_id"],
                         key_column="usos_id",
                         table="users"):  # or True (for debugging)
        db.create_user(**user_info)

        student_programmes = usos_connection.get(
            service="services/progs/student",
            user_id=user_info["usos_id"],
        )
        await asyncio.sleep(0.5)
        for programme in student_programmes:
            db.insert_study_programme(
                programme_id=programme["programme"]["id"],
                programme_name=programme["programme"]["description"]["pl"],
            )
            db.insert_user_programme(
                programme["programme"]["id"],
                user_id=user_info["usos_id"]
            )
        groups_participant = usos_connection.get(
            service="services/groups/user",
            fields="course_unit_id|group_number|class_type|class_type_id|"
                   "course_id|course_name|term_id|participants",
            active_terms=True,
        )
        await asyncio.sleep(0.5)
        active_terms = [
            term["id"]
            for term in groups_participant["terms"]
            if dt.date.today() < dt.date.fromisoformat(term["end_date"])
        ]
        unit_ids = []
        for active_term in active_terms:
            if not db.row_exists(key_value=active_term,
                                 key_column="usos_term_id",
                                 table="terms"):
                active_term_info = usos_connection.get(
                    service="services/terms/term",
                    term_id=active_term,
                    fields="name|start_date|end_date"
                )
                await asyncio.sleep(1)
                db.insert_term(active_term,
                               active_term_info["name"]["pl"],
                               active_term_info["start_date"],
                               active_term_info["end_date"])
            for group in groups_participant["groups"][active_term]:
                unit_ids.append(group["course_unit_id"])

                # Course
                db.upsert_course(group["course_id"],
                                 group["course_name"]["pl"],
                                 active_term)

                # Group types
                if not db.row_exists(key_value=group["class_type_id"],
                                     key_column="group_type_id",
                                     table="group_types"):
                    db.upsert_group_types(group_type_id=group["class_type_id"],
                                          group_type_name=group["class_type"]["pl"])

                # USOS unit id
                db.upsert_usos_units(usos_unit_id=group["course_unit_id"],
                                     course=group["course_id"],
                                     group_type=group["class_type_id"])

                unit_group_id = db.upsert_unit_group(group["course_unit_id"],
                                                     group["group_number"])

                # This user in groups
                db.insert_user_group(user_usos_id=user_info["usos_id"],
                                     unit_group_id=unit_group_id)

                # Students
                for student_info in group["participants"]:
                    student_info["usos_id"] = student_info.pop("id")
                    if not db.row_exists(key_value=student_info["usos_id"],
                                         key_column="usos_id",
                                         table="users"):
                        db.create_user(**student_info)
                        db.insert_user_group(user_usos_id=student_info["usos_id"],
                                             unit_group_id=unit_group_id)
                        db.insert_user_programme(
                            student_programmes[0]["programme"]["id"],
                            user_id=student_info["usos_id"]
                        )
        for unit_id in unit_ids:
            courses_unit_response = usos_connection.get(
                service="services/courses/unit",
                unit_id=unit_id,
                fields="id|course_id|term_id|"
                       "groups[group_number|class_type|class_type_id|lecturers]"
            )
            await asyncio.sleep(0.5)
            coordinators = usos_connection.get(
                service="services/courses/course_edition",
                course_id=courses_unit_response["course_id"],
                term_id=courses_unit_response["term_id"],
                fields="coordinators"
            )["coordinators"]
            await asyncio.sleep(0.5)
            for coordinator in coordinators:
                db.upsert_teacher(coordinator["id"],
                                  coordinator["first_name"],
                                  coordinator["last_name"])
                db.insert_course_manager(
                    course_id=courses_unit_response["course_id"],
                    teacher_id=coordinator["id"]
                )

            start_time, end_time = db.get_unit_term_info(courses_unit_response["term_id"])
            for group in courses_unit_response["groups"]:
                # Unit groups
                unit_group_index = db.upsert_unit_group(unit_id,
                                                        group["group_number"])

                # Teachers
                for lecturer in group["lecturers"]:
                    db.upsert_teacher(lecturer["id"],
                                      lecturer["first_name"],
                                      lecturer["last_name"])
                    db.insert_group_teacher(unit_group_index, lecturer["id"])

                for date in daterange(start_date=start_time, end_date=end_time, step=7):
                    timetable_group = usos_connection.get(
                        service="services/tt/classgroup",
                        unit_id=unit_id,
                        group_number=group["group_number"],
                        start=date.isoformat(),
                        days=7,
                        fields="start_time|end_time|room_number|room_id",
                    )
                    await asyncio.sleep(2)
                    for activity in timetable_group:
                        start_time_naive = dt.datetime.fromisoformat(activity["start_time"])
                        end_time_naive = dt.datetime.fromisoformat(activity["end_time"])
                        start_time_pl_tz = pl_tz.localize(start_time_naive, is_dst=True)
                        end_time_pl_tz = pl_tz.localize(end_time_naive, is_dst=True)

                        # Add room and building
                        if activity["room_id"] is not None and not db.row_exists(
                                key_value=activity["room_number"],
                                key_column="room_id",
                                table="rooms"
                        ):
                            room_building_info = usos_connection.get(
                                service="services/geo/room",
                                room_id=activity["room_id"],
                                fields="id|number|building|capacity",
                            )
                            await asyncio.sleep(1)
                            building_info = room_building_info["building"]
                            db.insert_building(
                                building_id=building_info["id"],
                                building_name=building_info["name"]["pl"],
                                longitude=building_info["location"]["long"],
                                latitude=building_info["location"]["lat"]
                            )
                            db.insert_room(room_id=room_building_info["number"],
                                           room_usos_id=room_building_info["id"],
                                           capacity=room_building_info["capacity"],
                                           building_id=building_info["id"])

                        # Activity
                        db.upsert_activities(
                            start_time=start_time_pl_tz,
                            end_time=end_time_pl_tz,
                            room=activity["room_number"],
                            unit_group=unit_group_index,
                        )
    usos_connection.logout()
