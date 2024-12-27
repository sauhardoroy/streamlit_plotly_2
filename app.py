import sqlite3 as s3
import threading

import pandas as pd
import streamlit as st
from speed_along_track_two_drivers import speed_along_track_plot
from speed_analysis_two_drivers import speed_telemetry_plot
from utils import get_corner_info, get_race_drivers, run_in_parallel

st.header("Data Vis")

race_with_drivers = get_race_drivers()

years_race_with_drivers = sorted(
    set([race_with_drivers[item][3] for item in range(len(race_with_drivers))]),
    reverse=True,
)[:1]

race_race_with_drivers = sorted(
    set(
        [
            race_with_drivers[item][2]
            for item in range(len(race_with_drivers))
            if race_with_drivers[item][3] in years_race_with_drivers
        ]
    ),
    reverse=False,
)

drivers_race_with_drivers = sorted(
    set(
        [
            race_with_drivers[item][5]
            for item in range(len(race_with_drivers))
            if race_with_drivers[item][3] in years_race_with_drivers
        ]
    ),
    reverse=False,
)

for key in ["year", "race", "driver1", "driver2"]:
    st.session_state.setdefault(key, None)


col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

year = col1.selectbox(
    "select year",
    years_race_with_drivers,
    placeholder="Enter Race",
)


st.session_state.year = year
race_race_with_drivers_filtered = sorted(
    set(
        [
            race_with_drivers[item][2]
            for item in range(len(race_with_drivers))
            if race_with_drivers[item][3] == st.session_state.year
        ]
    ),
    reverse=False,
)
race = col2.selectbox(
    "select race",
    race_race_with_drivers_filtered,
    placeholder="Enter Race",
)

st.session_state.race = race

corner_info = get_corner_info(race, year)
# race_details = load_session(year, race)
driver1_race_with_drivers_filtered = sorted(
    set(
        [
            race_with_drivers[item][5]
            for item in range(len(race_with_drivers))
            if race_with_drivers[item][3] == st.session_state.year
            and race_with_drivers[item][2] == st.session_state.race
        ]
    ),
    reverse=False,
)

driver1 = col3.selectbox(
    "select driver1",
    driver1_race_with_drivers_filtered,
)

st.session_state.driver1 = driver1
driver2_race_with_drivers_filtered = sorted(
    set(
        [
            race_with_drivers[item][5]
            for item in range(len(race_with_drivers))
            if race_with_drivers[item][3] == st.session_state.year
            and race_with_drivers[item][2] == st.session_state.race
            # and race_with_drivers[item][5] != driver1
        ]
    ),
    reverse=False,
)
driver2 = col4.selectbox(
    "select driver2",
    driver2_race_with_drivers_filtered,
)

st.session_state.driver2 = driver2

if st.session_state.driver2 and st.session_state.driver1:

    if driver1 == driver2:
        st.warning("Select Different Drivers")
    else:

        fig_speed_telemetry_plot, fig_speed_along_track_plot = run_in_parallel(
            [speed_telemetry_plot, speed_along_track_plot], driver1, driver2, year, race
        )
        # with st.expander(label="Expand to see All Actions"):
        #     st.dataframe(all_actions)

        # Streamlit display
        st.title("Driver Telemetry Analysis")
        try:
            st.plotly_chart(fig_speed_telemetry_plot, use_container_width=True)
        except Exception as e:
            st.error(f"An error occurred while generating the plots: {e}")

        try:
            st.plotly_chart(fig_speed_along_track_plot, use_container_width=True)
        except Exception as e:
            st.error(f"An error occurred while generating the plots: {e}")
        # col1, col2 = st.columns(2)
        # col1.plotly_chart(fig_speed_telemetry_plot, use_container_width=True)
        # col2.plotly_chart(fig_speed_along_track_plot, use_container_width=True)
