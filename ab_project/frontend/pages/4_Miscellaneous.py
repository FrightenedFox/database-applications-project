import streamlit as st

from ab_project.frontend.USOS_Main import init_connection


def main():
    st.markdown("# Inne")

    # New teacher
    st.subheader("Dodawanie nowego prowadzącego")
    with st.container():
        col1_inputs_teacher, col2_feedback_teacher = st.columns(2)
        with col1_inputs_teacher:
            teacher_first_name = st.text_input(
                label="Imię",
                placeholder="Podaj imię nowego prowadzącego",
                key="teacher_first_name",
            )
            teacher_last_name = st.text_input(
                label="Nazwisko",
                placeholder="Podaj nazwisko nowego prowadzącego",
                key="teacher_last_name",
            )
            if st.button(label="Dodaj", key="add_teacher_btn"):
                add_teacher_answer = st.session_state.db.call_procedure(
                    procedure_name_with_s_placeholders="dodaj_nowego_prowadzacego(%s, %s, '???')",
                    params=[
                        teacher_first_name,
                        teacher_last_name,
                    ],
                )
                if add_teacher_answer[1]:
                    col2_feedback_teacher.success(add_teacher_answer[0][0])
                else:
                    col2_feedback_teacher.error(add_teacher_answer[0])

    st.markdown("---")

    st.subheader("Dodawanie nowego budynku")
    # New building
    with st.container():
        col1_inputs_building, col2_feedback_building = st.columns(2)
        with col1_inputs_building:
            building_id = st.text_input(
                label="ID budynku",
                placeholder="V",
                key="building_id",
            )
            building_name = st.text_input(
                label="Nazwa budynku",
                placeholder="Budynek V - Regionalne Centrum Dydaktyczno-Konferencyjne i Biblioteczno-Administracyjne PRz",
                key="building_name",
            )
            building_latitude = st.number_input(
                label="Szerokość geograficzna",
                value=50.019044,
                format="%f",
                key="building_latitude",
            )
            building_longitude = st.number_input(
                label="Długość geograficzna",
                value=21.989185,
                format="%f",
                key="building_longitude",
            )
            if st.button(label="Dodaj", key="add_building_btn"):
                add_building_answer = st.session_state.db.call_procedure(
                    procedure_name_with_s_placeholders="dodaj_nowy_budynek(%s, %s, %s, %s, '???')",
                    params=[
                        building_id,
                        building_name,
                        building_longitude,
                        building_latitude
                    ],
                )
                if add_building_answer[1]:
                    col2_feedback_building.success(add_building_answer[0][0])
                else:
                    col2_feedback_building.error(add_building_answer[0])


if __name__ == "__main__":
    st.set_page_config(
        page_title="USOS Room reservation",
    )
    if "db" not in st.session_state:
        st.session_state["db"] = init_connection()
    main()
