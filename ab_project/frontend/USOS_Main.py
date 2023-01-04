import streamlit as st

from ab_project.db import UsosDB
from ab_project.logging_setup import initialize_logging


@st.experimental_singleton
def init_connection():
    initialize_logging()
    database = UsosDB()
    database.connect()
    return database


def main():
    st.markdown("# Main page 🎈")
    st.sidebar.markdown("# Main page 🎈")


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS Main",
    )
    main()
