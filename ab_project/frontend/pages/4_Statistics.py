from math import sqrt

import plotly.express as px
import streamlit as st

from ab_project.frontend.USOS_Main import init_connection


def main():
    st.markdown("# Statystyki")

    building_distances_df = st.session_state.db.get_distances_between_buildings()
    building_names = building_distances_df.build1.unique()
    n_buildings = int(sqrt(len(building_distances_df)))
    fig = px.imshow(building_distances_df.values.reshape(n_buildings, n_buildings, 3)[:, :, 2],
                    labels=dict(color="Odległość [m]"),
                    x=building_names,
                    y=building_names,
                    title="Odległości między budynkami Politechniki Rzeszowskiej"
                    )
    st.plotly_chart(fig)

    teachers_hours_df = st.session_state.db.get_teachers_working_hours()
    fig2 = px.histogram(teachers_hours_df, x="teacher", y="work_hours")
    fig2.update_layout(
        title_text='Spędzony czas prowadzących z IiAD',
        xaxis_title_text='Prowadzący',
        yaxis_title_text='Łączna liczba godzin pracy [g]',
        bargap=0.2,
        bargroupgap=0.1
    )
    st.plotly_chart(fig2)


if __name__ == '__main__':
    st.set_page_config(
        page_title="USOS Statistics",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
