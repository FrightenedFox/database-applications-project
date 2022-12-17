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
    course_name = st.sidebar.selectbox(label="Przedmiot", options=courses_df.course_name)
    get_course_id = lambda course_name_: courses_df[courses_df.course_name == course_name_].course_id.iat[0]

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
        get_unit_group_id = lambda unit_group_number_: \
            unit_groups_df[unit_groups_df.group_number == unit_group_number_].unit_group_id.iat[0]


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS User management",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
