import streamlit as st

from ab_project.frontend.USOS_Main import init_connection


def main():
    st.markdown("# Zarządzanie użytkownikiem")
    st.sidebar.header("Filtry")

    programme_id = st.sidebar.selectbox(label="Kierunek studiów",
                                        options=st.session_state.db.pandas_get_all_from_table(
                                            table="study_programmes",
                                            column="programme_id"
                                        ).programme_id)

    terms_df = st.session_state.db.get_terms(programme_id=programme_id)
    term_name = st.sidebar.selectbox(label="Semestr",
                                     options=terms_df.term_name)
    get_term_id = lambda term_name_: terms_df[terms_df.term_name == term_name_].usos_term_id[0]

    courses_df = st.session_state.db.get_courses(programme_id=programme_id,
                                                 usos_term_id=get_term_id(term_name))
    course_name = st.sidebar.selectbox(label="Przedmiot",
                                       options=courses_df.course_name)
    get_course_id = lambda course_name_: courses_df[courses_df.course_name == course_name_].course_id[0]

    group_types_df = st.session_state.db.get_group_types(course_id=get_course_id(course_name),
                                                         usos_term_id=get_term_id(term_name))
    st.write(type(group_types_df))


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS User management",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
