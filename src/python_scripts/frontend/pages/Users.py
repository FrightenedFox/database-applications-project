import datetime as dt

import streamlit as st

st.set_page_config(
    layout="wide"
)

with st.sidebar:
    st.write("# Filters")
    # TODO: Add min date
    dates = st.date_input(
        "Joined:",
        value=(dt.date.today() - dt.timedelta(days=1), dt.date.today())
    )
    # #TODO: Check if dates is tuple or datetime
    # TODO: select real study programmes
    programme = st.selectbox(
        "Study programme:",
        options=("Any", "x", "d")
    )


st.write("# Dataframe with users here")

# col1, col2 = st.columns([1, 3])
#
# with col1:
#     # TODO: Is that necessary?
#     pass
#
# with col2:
#     st.write("# Users")
#     # TODO: Add dataframe
#     pass
