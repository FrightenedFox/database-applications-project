import logging
import datetime as dt

from usosapi.usosapi import USOSAPIConnection
from config.config import app_config


def pull_data():
    usos_connection = USOSAPIConnection(
        api_base_address=app_config.usosapi.api_base_address,
        consumer_key=app_config.usosapi.consumer_key,
        consumer_secret=app_config.usosapi.consumer_secret
    )

    print(usos_connection.get_authorization_url())
    usos_connection.authorize_with_pin(input("Enter pin code: "))
    print(f"Authorization is successful: {usos_connection.is_authorized()}")

    user_info = usos_connection.current_identity()

    student_programmes = usos_connection.get(
        service="services/progs/student",
        user_id=user_info["id"],
    )
    for programme in student_programmes:
        print(programme)
        # db.insert_study_programme(
        #     programme_id=programme["programme"]["id"],
        #     programme_name=programme["programme"]["description"]["pl"],
        # )

    groups_participant = usos_connection.get(
        service="services/groups/participant",
        fields="course_unit_id|group_number|class_type|class_type_id|"
               "course_id|course_name|term_id|lecturers",
        active_terms=True,
    )
    active_terms = [
        term["id"]
        for term in groups_participant["terms"]
        if dt.date.today() < dt.date.fromisoformat(term["end_date"])
    ]
    print(active_terms)
    for active_term in active_terms:
        for group in groups_participant["groups"][active_term]:
            print(group)
