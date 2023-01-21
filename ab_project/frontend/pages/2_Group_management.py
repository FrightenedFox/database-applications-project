import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from ab_project.frontend.USOS_Main import init_connection


def main():
    st.markdown("# Zarządzanie grupą")
    st.sidebar.header("Filtry")

    programme_id = st.sidebar.selectbox(
        label="Kierunek studiów",
        options=st.session_state.db.pandas_get_all_from_table(
            table="study_programmes", column="programme_id"
        ).programme_id,
    )

    terms_df = st.session_state.db.get_terms(programme_id=programme_id)
    term_name = st.sidebar.selectbox(label="Semestr", options=terms_df.term_name)
    get_term_id = lambda term_name_: terms_df[
        terms_df.term_name == term_name_
        ].usos_term_id.iat[0]

    term_start_date = terms_df[
        terms_df.usos_term_id == get_term_id(term_name)
        ].start_date.iat[0]
    term_end_date = terms_df[
        terms_df.usos_term_id == get_term_id(term_name)
        ].end_date.iat[0]

    courses_df = st.session_state.db.get_courses(
        programme_id=programme_id, usos_term_id=get_term_id(term_name)
    )
    courses_df.loc[:, "unique_readable_course_id"] = courses_df.apply(
            lambda row: f"{row.course_name} [{row.course_id}]",
            axis=1,
        )
    unique_readable_course_id = st.selectbox(label="Przedmiot", options=courses_df.unique_readable_course_id)
    course_id = courses_df[courses_df.unique_readable_course_id == unique_readable_course_id
        ].course_id.iat[0]

    col1_group_type, col2_group_number = st.columns(2)
    with col1_group_type:
        group_types_df = st.session_state.db.get_group_types(
            course_id=course_id, usos_term_id=get_term_id(term_name)
        )
        group_type_name = st.selectbox(
            label="Typ zajęć", options=group_types_df.group_type_name
        )
        get_group_type_id = lambda group_type_name_: group_types_df[
            group_types_df.group_type_name == group_type_name_
            ].group_type_id.iat[0]

    with col2_group_number:
        unit_groups_df = st.session_state.db.get_unit_groups(
            course_id=course_id,
            usos_term_id=get_term_id(term_name),
            group_type=get_group_type_id(group_type_name),
        )
        unit_group_number = st.selectbox(
            label="Numer grupy", options=unit_groups_df.group_number
        )
        get_unit_group_id = lambda: int(
            unit_groups_df[
                unit_groups_df.group_number == unit_group_number
                ].unit_group_id.iat[0]
        )
        unit_group_id = int(
            unit_groups_df[
                unit_groups_df.group_number == unit_group_number
                ].unit_group_id.iat[0]
        )
        # NOTE: można nie używać lambdy

    st.markdown("---")

    st.subheader("Zmiana prowadzącego")
    con_change_teacher = st.container()
    with con_change_teacher:
        current_group_teacher = st.session_state.db.get_unit_group_teacher(
            unit_group_id
        )
        current_teacher_info = st.info(
            f"""
        Aktualny prowadzący grupy:\t **{current_group_teacher[1]} {current_group_teacher[2]}**
        """
        )
        teachers_df = st.session_state.db.pandas_get_all_from_table(table="teachers")
        teachers_df.loc[:, "unique_readable_teacher_id"] = teachers_df.apply(
            lambda row: f"{row.first_name} {row.last_name} [{row.teacher_usos_id}]",
            axis=1,
        )
        teachers_df = teachers_df.sort_values(
            ["last_name", "first_name", "teacher_usos_id"]
        ).reset_index(drop=True)
        new_group_teacher_readable_name = st.selectbox(
            label="Nowy prowadzący:",
            options=teachers_df.unique_readable_teacher_id,
        )
        new_group_teacher_id = int(
            teachers_df[
                teachers_df.unique_readable_teacher_id
                == new_group_teacher_readable_name
                ].teacher_usos_id.iat[0]
        )

        if st.button("Zmień prowadzącego"):
            teacher_change_answer = st.session_state.db.call_procedure(
                procedure_name_with_s_placeholders="zmien_prowadzacego(%s, %s, '???')",
                params=[unit_group_id, new_group_teacher_id],
            )
            current_group_teacher = st.session_state.db.get_unit_group_teacher(
                unit_group_id
            )
            current_teacher_info.info(
                f"""
            Aktualny prowadzący grupy:\t **{current_group_teacher[1]} {current_group_teacher[2]}**
            """
            )
            if teacher_change_answer[1]:
                st.success(teacher_change_answer[0][0])
            else:
                st.error(teacher_change_answer[0])

    st.markdown("---")

    st.subheader("Dodanie nowego zajęcia")
    add_new_activity = st.container()
    with add_new_activity:
        rooms_df = (
            st.session_state.db.pandas_get_all_from_table(table="rooms")
            .sort_values(["building_id", "room_id"])
            .reset_index(drop=True)
        )
        new_activity_room_id = st.selectbox(label="Sala:", options=rooms_df.room_id)
        (
            col1_new_activity_date,
            col2_new_activity_start_time,
            col3_new_activity_end_time,
        ) = st.columns(3)
        with col1_new_activity_date:
            new_activity_date = st.date_input(
                label="Data:", min_value=term_start_date, max_value=term_end_date
            )
        with col2_new_activity_start_time:
            new_activity_start_time = st.time_input(label="Czas rozpoczęcia zajęcia:")
        with col3_new_activity_end_time:
            new_activity_end_time = st.time_input(label="Czas zakończenia zajęcia:")
        if st.button("Dodaj zajęcie"):
            add_new_activity_answer = st.session_state.db.call_procedure(
                procedure_name_with_s_placeholders="dodaj_nowe_zajecia(%s, %s, %s, %s, '???')",
                params=[
                    unit_group_id,
                    new_activity_room_id,
                    dt.datetime.combine(new_activity_date, new_activity_start_time),
                    dt.datetime.combine(new_activity_date, new_activity_end_time),
                ],
            )
            if add_new_activity_answer[1]:
                st.success(add_new_activity_answer[0][0])
            else:
                st.error(add_new_activity_answer[0])

    st.markdown("---")

    st.subheader("Manipulacje pojedynczym zajęciem")
    add_new_activity = st.container()
    with add_new_activity:
        group_activities_df = st.session_state.db.get_unit_group_activities(unit_group_id)
        group_activities_df.loc[:, "human_readable_name"] = group_activities_df.apply(
            lambda row: f"(ID {row.activity_id}) | {row.start_time} -- {row.end_time} | {row.room}", axis=1)
        activity_filtr_dates = st.date_input(
            label="Filtruj zajęcia według daty:",
            min_value=term_start_date,
            max_value=term_end_date,
            value=(term_start_date, term_end_date),
        )
        if len(activity_filtr_dates) == 2:
            group_activities_df_filtered = group_activities_df[
                np.logical_and(
                    group_activities_df.start_time.dt.date
                    >= pd.to_datetime(activity_filtr_dates[0]).date(),
                    group_activities_df.end_time.dt.date
                    <= pd.to_datetime(activity_filtr_dates[1]).date(),
                )
            ]
        else:
            group_activities_df_filtered = group_activities_df[
                group_activities_df.start_time.dt.date == pd.to_datetime(activity_filtr_dates[0]).date()
                ]
        if len(group_activities_df_filtered) < 1:
            st.warning("Wybrana grupa nie ma zajęć z wybranego przedmiotu w wybranym odcinku czasowym.")
        else:
            modify_activity_human_readable_name = st.selectbox(label="Zajęcie",
                                                               options=group_activities_df_filtered.human_readable_name)
            modify_activity = group_activities_df_filtered[
                                  group_activities_df_filtered.human_readable_name == modify_activity_human_readable_name
                                  ].iloc[0, :]

            tab1_change_time, tab2_delete = st.tabs(["Zmień czas zajęć", "Usuń zajęcie"])
            with tab1_change_time:
                (
                    col1_activity_new_date,
                    col2_activity_new_start_time,
                    col3_activity_new_end_time,
                ) = st.columns(3)
                with col1_activity_new_date:
                    activity_new_date = st.date_input(
                        label="Nowa data zajęcia:",
                        min_value=term_start_date,
                        max_value=term_end_date,
                        value=modify_activity.start_time
                    )
                with col2_activity_new_start_time:
                    activity_new_start_time = st.time_input(label="Nowy czas rozpoczęcia zajęcia:",
                                                            value=modify_activity.start_time)
                with col3_activity_new_end_time:
                    activity_new_end_time = st.time_input(label="Nowy czas zakończenia zajęcia:",
                                                          value=modify_activity.end_time)
                if st.button("Zapisz zmiany"):
                    change_activity_time_answer = st.session_state.db.call_procedure(
                        procedure_name_with_s_placeholders="przenieś_zajecia_w_czasie(%s, %s, %s, '???')",
                        params=[
                            int(modify_activity.activity_id),
                            dt.datetime.combine(activity_new_date, activity_new_start_time),
                            dt.datetime.combine(activity_new_date, activity_new_end_time),
                        ],
                    )
                    if change_activity_time_answer[1]:
                        st.success(change_activity_time_answer[0][0])
                    else:
                        st.error(change_activity_time_answer[0])
                        # TODO: Nie mozna przeniesc zajec, poniewaz w danym czasie sala jest zajeta, gdy przenosimy zajęcia w to samo miejsce.

            with tab2_delete:
                if st.button("Usuń zajęcie"):
                    st.session_state.db.delete_activity(int(modify_activity.activity_id))
                    st.info("Zajęcie zostało usunięte. Żeby zobaczyć zmiany zaktualizuj stronę lub kliknij `R`.")


if __name__ == "__main__":
    st.set_page_config(
        page_title="USOS group management",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
