import streamlit as st

from ab_project.frontend.USOS_Main import init_connection

def main():
    st.markdown("# Rezerwacja sali")


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS Room reservation",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()