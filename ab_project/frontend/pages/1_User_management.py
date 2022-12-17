import streamlit as st
from ab_project.frontend.USOS_Main import init_connection

def main():
    st.set_page_config(
        page_title="USOS User management",
    )
    st.markdown("# Zarządzanie użytkownikiem")
    st.sidebar.markdown("# Zarządzanie użytkownikiem")
    st.sidebar.selectbox(label="Wybierz kierunek studiów", options=st.session_state.db.get_all_from_table(
        table="study_programme",
        column="programme_id"
    ))

if __name__ == '__main__':
    if "db" not in st.session_state:
        st["db"] = init_connection()
    main()