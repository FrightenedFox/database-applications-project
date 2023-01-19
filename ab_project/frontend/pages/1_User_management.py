import streamlit as st

from ab_project.frontend.USOS_Main import init_connection


def main():
    st.markdown("# Zarządzanie studentem")
    st.sidebar.header("Filtry")

    programme_id = st.sidebar.selectbox(label="Kierunek studiów",
                                        options=st.session_state.db.pandas_get_all_from_table(
                                            table="study_programmes",
                                            column="programme_id"
                                        ).programme_id)

    terms_df = st.session_state.db.get_terms(programme_id=programme_id)
    term_name = st.sidebar.selectbox(label="Semestr", options=terms_df.term_name)
    term_id = terms_df[terms_df.term_name == term_name].usos_term_id.iat[0]

    users_df = st.session_state.db.get_users(usos_term_id=term_id, programme_id=programme_id)
    users_df.loc[:, "unique_readable_user_id"] = users_df.apply(
        lambda row: f"{row.first_name} {row.last_name} [{row.usos_id}]", axis=1)
    vitaliis_index = int(users_df[users_df.usos_id == 234394].index[0])
    unique_readable_user_id = st.selectbox(label="Student", options=users_df.unique_readable_user_id, index=vitaliis_index)
    user_usos_id = int(users_df[users_df.unique_readable_user_id == unique_readable_user_id].usos_id.iat[0])

    st.markdown("---")

    st.subheader("Przepisanie studenta do innej grupy")
    con_move_student = st.container()
    with con_move_student:
        tab1_one_subject, tab2_all_groups_of_type = st.tabs(["Dla jednego przedmiotu", "Dla typu grupy"])
        with tab1_one_subject:

            col1_group_selection, col2_group_selection = st.columns(2)
            with col1_group_selection:
                courses_df = st.session_state.db.get_courses(programme_id=programme_id, usos_term_id=term_id)
                course_name = st.selectbox(label="Przedmiot", options=courses_df.course_name,
                                           key="single_subject_course_name")
                course_id = courses_df[courses_df.course_name == course_name].course_id.iat[0]

            with col2_group_selection:
                group_types_df = st.session_state.db.get_group_types(course_id=course_id,
                                                                     usos_term_id=term_id)
                group_type_name = st.selectbox(label="Typ zmienianej grupy", options=group_types_df.group_type_name,
                                               key="single_subject_group_type")
                group_type_id = group_types_df[group_types_df.group_type_name == group_type_name].group_type_id.iat[0]

            unit_groups_df = st.session_state.db.get_unit_groups(course_id=course_id,
                                                                 usos_term_id=term_id,
                                                                 group_type=group_type_id)
            user_unit_group = st.session_state.db.get_user_unit_group(
                usos_unit_id=int(unit_groups_df.usos_unit_id.iat[0]), usos_user_id=user_usos_id)
            if user_unit_group is not None:
                old_unit_group_id, _, old_group_number = user_unit_group

                with col1_group_selection:
                    group_display = st.info(f"Aktualny numer grupy: **{old_group_number}**")

                with col2_group_selection:
                    unit_group_number = st.selectbox(label="Nowy numer grupy", options=unit_groups_df.group_number,
                                                     key="single_subject_group_number")
                    new_unit_group_id = int(
                        unit_groups_df[unit_groups_df.group_number == unit_group_number].unit_group_id.iat[0])
                        
                with col1_group_selection:
                    if st.button("Przepisz studenta do nowej grupy", key="single_subject_accept_button"):
                        if old_unit_group_id != new_unit_group_id:
                            change_single_subject_group_answer = st.session_state.db.call_procedure(
                                procedure_name_with_s_placeholders="przenies_studenta_do_innej_grupy_na_jedne_zajecia(%s, %s, %s, '???')",
                                params=[
                                    user_usos_id,
                                    old_unit_group_id,
                                    new_unit_group_id,
                                ],
                            )
                            if change_single_subject_group_answer[1]:
                                tab1_one_subject.success(change_single_subject_group_answer[0][0])
                                group_display.info(f"Aktualny numer grupy: **{unit_group_number}**")
                            else:
                                tab1_one_subject.error(change_single_subject_group_answer[0])
                        else:
                            tab1_one_subject.warning(
                                "Nowa grupa nie różni się od już aktualnej grupy. Nie wprowadzono zmian.")

            else:
                st.warning("Osoba nie jest przypisana do żadnej grupy dla wybranego przedmiotu.")

        with tab2_all_groups_of_type:
            col1_group_type, col2_group_number = st.columns(2)
            with col1_group_type:
                all_group_types_df = st.session_state.db.pandas_get_all_from_table(table="group_types")
                group_type_name = st.selectbox(label="Typ grupy:  ", options=all_group_types_df.group_type_name,
                                               key="all_subjects_group_type")
                group_type_id = \
                    all_group_types_df[all_group_types_df.group_type_name == group_type_name].group_type_id.iat[0]

            with col2_group_number:
                group_numbers = st.session_state.db.get_group_numbers_for_group_type(
                    group_type=group_type_id).group_number.values
                new_group_number = int(
                    st.selectbox(label="Nowy numer grupy", options=group_numbers, key="all_subjects_group_number"))

            if st.button("Przepisz studenta do nowej grupy", key="all_subjects_accept_button"):
                change_all_subjects_group_answer = st.session_state.db.call_procedure(
                    procedure_name_with_s_placeholders="przenies_studenta_na_wszystkie_zajecia(%s, %s, %s, '???')",
                    params=[
                        user_usos_id,
                        group_type_id,
                        new_group_number,
                    ],
                )
                if change_all_subjects_group_answer[1]:
                    st.success(change_all_subjects_group_answer[0][0])
                else:
                    st.error(change_all_subjects_group_answer[0])


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS User management",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
