import sqlite3 as s3

import pandas as pd
import streamlit as st
from speed_along_track_two_drivers import speed_along_track_plot
from speed_analysis_two_drivers import speed_telemetry_plot
from utils import run_in_parallel


@st.dialog("Data Viz", width="large")
def plot_dialog(driver1, driver2, year, race, qualification1, qualification2):

    fig_speed_telemetry_plot, fig_speed_along_track_plot = run_in_parallel(
        [speed_telemetry_plot, speed_along_track_plot],
        driver1,
        driver2,
        year,
        race,
        qualification1,
        qualification2,
    )

    st.html("<span class='big-dialog'>")

    st.title("Driver Telemetry Analysis")
    try:
        st.plotly_chart(fig_speed_telemetry_plot, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while generating the plots: {e}")

    try:
        st.plotly_chart(fig_speed_along_track_plot, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while generating the plots: {e}")
    st.html("</span>")


def calling_plot_dialog(driver1, driver2, year, race, qualification1, qualification2):
    plot_dialog(driver1, driver2, year, race, qualification1, qualification2)
