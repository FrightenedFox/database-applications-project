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
    courses_df = st.session_state.db.get_courses(programme_id=programme_id,
                                                 usos_term_id=terms_df[terms_df.term_name == term_name].term_id[0])
    course_name = st.sidebar.selectbox(label="Przedmiot",
                                       options=courses_df.course_name)


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS User management",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
