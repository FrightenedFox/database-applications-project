import streamlit as st
from ab_project.db import UsosDB
@st.experimental_singleton
def init_connection():
    database = UsosDB()
    database.connect()
    return database


st.set_page_config(
    page_title="USOS Main",
)
st.markdown("# Main page 🎈")
st.sidebar.markdown("# Main page 🎈")
