import sqlite3 as s3

import pandas as pd
import streamlit as st
from custom_streamlit_utils import calling_plot_dialog
from utils import connection, get_corner_info, normalize_string

st.header("Data Visualization")

st.markdown(
    """
<style>
div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
    width: 80vw;
    height: 800vh;
    background_color: "white"
}
.center {
text-align: center
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>.element-container:has(#button-after) + div button {
    background: #242424;
    color: white;
    padding: 1rem 1.5rem;
    border: white;
    cursor: pointer;
    font-size: 1rem;
    text-align: center;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.2s ease-in-out;
    }
    .element-container:has(#button-after) + div button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(161, 156, 156, 0.1);
    text-align: center;
    background:white;
    color: #e10600;
    transition: all 0.2s ease-in-out;
    }
 </style>""",
    unsafe_allow_html=True,
)


cursor = connection()

for key in ["year", "race", "driver1", "driver2", "qualification1", "qualification2"]:
    st.session_state.setdefault(key, None)


col1, col2 = st.columns([1, 3])
years_data = [2024]
year = col1.selectbox(
    "select year",
    years_data,
    placeholder="Enter Race",
)


st.session_state.year = year

race_list = cursor.execute(
    f"select show_name, name from race_events_view where year = {st.session_state.year}"
).fetchall()


race_show_list = [item[0] for item in race_list]

race = col2.selectbox(
    "select race",
    race_show_list,
    placeholder="Enter Race",
)

st.session_state.race = [
    normalize_string(item[1]) for item in race_list if item[0] == race
][0]

corner_info = get_corner_info(race, year)
driver_list = cursor.execute(
    f"select show_name, name, qualificationround from drivers_in_race_in_year_view where racename = '{st.session_state.race}' and year = {st.session_state.year}"
).fetchall()

driver_show_list = [item[0] for item in driver_list]

col3, col4 = st.columns([3, 1])
driver1 = col3.selectbox(
    "select driver1",
    driver_show_list,
)

st.session_state.driver1 = [
    normalize_string(item[1]) for item in driver_list if item[0] == driver1
][0]

col5, col6 = st.columns([3, 1])
driver2 = col5.selectbox(
    "select driver2",
    driver_show_list,
)

st.session_state.driver2 = [
    normalize_string(item[1]) for item in driver_list if item[0] == driver2
][0]


driver2 = st.session_state.driver2
driver1 = st.session_state.driver1


st.session_state.qualification1 = [
    item[2] for item in driver_list if item[1] == driver1
][0]

# col5, col6 = st.columns([1, 1])
if st.session_state.qualification1 == "Q3":
    st.session_state.qualification1 = col4.selectbox(
        f"Select Qualification",
        ["Q1", "Q2", "Q3"],
    )
elif st.session_state.qualification1 == "Q2":
    st.session_state.qualification1 = col4.selectbox(
        f"Select Qualification",
        ["Q1", "Q2"],
    )
elif st.session_state.qualification1 == "Q1":
    st.session_state.qualification1 = col4.selectbox(
        f"Select Qualification",
        ["Q1"],
    )
else:
    col4.warning("Does not have qualification round")

st.session_state.qualification2 = [
    item[2] for item in driver_list if item[1] == driver2
][0]
if st.session_state.qualification2 == "Q3":
    st.session_state.qualification2 = col6.selectbox(
        f"Select  Qualification",
        ["Q1", "Q2", "Q3"],
    )
elif st.session_state.qualification2 == "Q2":
    st.session_state.qualification2 = col6.selectbox(
        f"Select  Qualification",
        ["Q1", "Q2"],
    )
elif st.session_state.qualification2 == "Q1":
    st.session_state.qualification2 = col6.selectbox(
        f"Select  Qualification",
        ["Q1"],
    )
else:
    col5.warning("Does not have qualification round")


if (
    st.session_state.driver1 == st.session_state.driver2
    and st.session_state.qualification1 == st.session_state.qualification2
):
    st.warning("Select Different Drivers or Different Qualifying Rounds")
else:
    if "plot_dialog" not in st.session_state:
        with st.container():
            cola, colb, colc = st.columns([0.23, 0.6, 0.17])

            # st.header(f"Open Dashboard:")
            st.markdown(
                '<h2 style="text-align: center;">Open Dashboard</h2>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<span class = "center" id="button-after">', unsafe_allow_html=True
            )
            cola, colb, colc = st.columns([0.27, 0.6, 0.13])
            if colb.button(
                f"{driver1} {st.session_state.qualification1}, {driver2} {st.session_state.qualification2}"
            ):
                calling_plot_dialog(
                    st.session_state.driver1,
                    st.session_state.driver2,
                    st.session_state.year,
                    st.session_state.race,
                    st.session_state.qualification1,
                    st.session_state.qualification2,
                )
            st.markdown("</span>", unsafe_allow_html=True)
