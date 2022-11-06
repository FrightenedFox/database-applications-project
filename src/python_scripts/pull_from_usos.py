import datetime as dt
import logging

from config.config import app_config
from db import UsosDB
from usosapi.usosapi import USOSAPIConnection


def pull_data(db: UsosDB):
    usos_connection = USOSAPIConnection(
        api_base_address=app_config.usosapi.api_base_address,
        consumer_key=app_config.usosapi.consumer_key,
        consumer_secret=app_config.usosapi.consumer_secret
    )

    print(usos_connection.get_authorization_url())
    usos_connection.authorize_with_pin(input("Enter pin code: "))
    logging.info(f"Authorization is successful: {usos_connection.is_authorized()}")

    user_info = usos_connection.current_identity()
    user_info["usos_id"] = user_info.pop("id")
    if not db.row_exists(key_value=user_info["usos_id"],
                         key_column="usos_id",
                         table="users") or True:
        # TODO: remove or TRUE
        db.create_user(**user_info)

        student_programmes = usos_connection.get(
            service="services/progs/student",
            user_id=user_info["usos_id"],
        )
        for programme in student_programmes:
            db.insert_study_programme(
                programme_id=programme["programme"]["id"],
                programme_name=programme["programme"]["description"]["pl"],
            )

        groups_participant = usos_connection.get(
            service="services/groups/participant",
            fields="course_unit_id|group_number|class_type|class_type_id|"
                   "course_id|course_name|term_id|lecturers|participants",
            active_terms=True,
        )
        active_terms = [
            term["id"]
            for term in groups_participant["terms"]
            if dt.date.today() < dt.date.fromisoformat(term["end_date"])
        ]
        print(active_terms)
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

                # No NEED, do it later with services/groups/group

                for student_info in group["participants"]:
                    student_info["usos_id"] = student_info.pop("id")
                    if not db.row_exists(key_value=student_info["usos_id"],
                                         key_column="usos_id",
                                         table="users"):
                        db.create_user(**student_info)

        for unit_id in unit_ids:
            courses_unit_response = usos_connection.get(
                service="services/courses/unit",
                unit_id=unit_id,
                fields="id|groups[group_number|class_type|class_type_id|lecturers]"
            )
            print(courses_unit_response)

        # print(unit_ids)

