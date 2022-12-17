import datetime as dt

import streamlit as st

from ab_project.frontend.USOS_Main import init_connection


def main():
    st.markdown("# Zarządzanie grupą")
    st.sidebar.header("Filtry")

    programme_id = st.sidebar.selectbox(label="Kierunek studiów",
                                        options=st.session_state.db.pandas_get_all_from_table(
                                            table="study_programmes",
                                            column="programme_id"
                                        ).programme_id)

    terms_df = st.session_state.db.get_terms(programme_id=programme_id)
    term_name = st.sidebar.selectbox(label="Semestr", options=terms_df.term_name)
    get_term_id = lambda term_name_: terms_df[terms_df.term_name == term_name_].usos_term_id.iat[0]

    courses_df = st.session_state.db.get_courses(programme_id=programme_id, usos_term_id=get_term_id(term_name))
    course_name = st.selectbox(label="Przedmiot", options=courses_df.course_name)
    get_course_id = lambda course_name_: courses_df[courses_df.course_name == course_name_].course_id.iat[0]
    # NOTE: sort courses

    col1_group_type, col2_group_number = st.columns(2)
    with col1_group_type:
        group_types_df = st.session_state.db.get_group_types(course_id=get_course_id(course_name),
                                                             usos_term_id=get_term_id(term_name))
        group_type_name = st.selectbox(label="Typ zajęć", options=group_types_df.group_type_name)
        get_group_type_id = lambda group_type_name_: \
            group_types_df[group_types_df.group_type_name == group_type_name_].group_type_id.iat[0]

    with col2_group_number:
        unit_groups_df = st.session_state.db.get_unit_groups(course_id=get_course_id(course_name),
                                                             usos_term_id=get_term_id(term_name),
                                                             group_type=get_group_type_id(group_type_name))
        unit_group_number = st.selectbox(label="Numer grupy", options=unit_groups_df.group_number)
        get_unit_group_id = lambda: \
            int(unit_groups_df[unit_groups_df.group_number == unit_group_number].unit_group_id.iat[0])
        unit_group_id = int(unit_groups_df[unit_groups_df.group_number == unit_group_number].unit_group_id.iat[0])
        # NOTE: można nie używać lambdy

    st.markdown("---")

    st.subheader("Zmiana prowadzącego")
    con_change_teacher = st.container()
    with con_change_teacher:
        current_group_teacher = st.session_state.db.get_unit_group_teacher(unit_group_id)
        current_teacher_info = st.info(f"""
        Aktualny prowadzący grupy:\t **{current_group_teacher[1]} {current_group_teacher[2]}**
        """)
        teachers_df = st.session_state.db.pandas_get_all_from_table(table="teachers")
        teachers_df.loc[:, "unique_readable_teacher_id"] = teachers_df.apply(
            lambda row: f"{row.first_name} {row.last_name} [{row.teacher_usos_id}]", axis=1)
        teachers_df = teachers_df.sort_values(["last_name", "first_name", "teacher_usos_id"]).reset_index(drop=True)
        new_group_teacher_readable_name = st.selectbox(label="Nowy prowadzący:",
                                                       options=teachers_df.unique_readable_teacher_id,
                                                       )
        new_group_teacher_id = int(
            teachers_df[teachers_df.unique_readable_teacher_id == new_group_teacher_readable_name].teacher_usos_id.iat[
                0])

        if st.button("Zmień prowadzącego"):
            teacher_change_answer = st.session_state.db.call_procedure(
                procedure_name_with_s_placeholders="zmien_prowadzacego(%s, %s, '???', TRUE)",
                params=[unit_group_id, new_group_teacher_id]
            )
            current_group_teacher = st.session_state.db.get_unit_group_teacher(unit_group_id)
            current_teacher_info.info(f"""
            Aktualny prowadzący grupy:\t **{current_group_teacher[1]} {current_group_teacher[2]}**
            """)
            if teacher_change_answer[1]:
                st.success(teacher_change_answer[0])
            else:
                st.error(teacher_change_answer[0])

    st.markdown("---")

    st.subheader("Dodanie nowego zajęcia")
    add_new_activity = st.container()
    with add_new_activity:
        rooms_df = st.session_state.db.pandas_get_all_from_table(table="rooms").sort_values(
            ["building_id", "room_id"]).reset_index(drop=True)
        new_activity_room_id = st.selectbox(label="Sala:", options=rooms_df.room_id)
        col1_new_activity_date, col2_new_activity_start_time, col3_new_activity_end_time = st.columns(3)
        with col1_new_activity_date:
            new_activity_date = st.date_input(label="Data:",
                                              min_value=
                                              terms_df[terms_df.usos_term_id == get_term_id(term_name)].start_date.iat[
                                                  0],
                                              max_value=
                                              terms_df[terms_df.usos_term_id == get_term_id(term_name)].end_date.iat[0])
        with col2_new_activity_start_time:
            new_activity_start_time = st.time_input(label="Czas rozpoczęcia zajęcia:")
        with col3_new_activity_end_time:
            new_activity_end_time = st.time_input(label="Czas zakończenia zajęcia:")
        if st.button("Dodaj zajęcie"):
            if new_activity_end_time <= new_activity_start_time:
                st.error("Czas rozpoczęcia zajęć musi być większy lub równy czasu zakończenia zajęć")
                # TODO: przenieść do procedury w SQL
            else:
                add_new_activity_answer = st.session_state.db.call_procedure(
                    procedure_name_with_s_placeholders="dodaj_nowe_zajecia(%s, %s, %s, %s, '???', TRUE)",
                    params=[
                        unit_group_id,
                        new_activity_room_id,
                        dt.datetime.combine(new_activity_date, new_activity_start_time),
                        dt.datetime.combine(new_activity_date, new_activity_end_time)
                    ]
                )
                if add_new_activity_answer[1]:
                    st.success(add_new_activity_answer[0])
                else:
                    st.error(add_new_activity_answer[0])

    st.markdown("---")


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS group management",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
