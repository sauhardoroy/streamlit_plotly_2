import sqlite3 as s3

import pandas as pd
import streamlit as st
from lap_run_two_drivers import lap_plot
from speed_along_track_two_drivers import speed_along_track_plot
from speed_analysis_two_drivers import speed_telemetry_plot
from utils import run_in_parallel


@st.dialog("Data Viz", width="large")
def dialog_function(fig1, fig2, fig3):

    st.html("<span class='big-dialog'>")

    st.title("Driver Telemetry Analysis")

    try:
        st.plotly_chart(fig3, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while generating the plots: {e}")
    try:
        st.plotly_chart(fig1, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while generating the plots: {e}")
    try:
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while generating the plots: {e}")

    st.html("</span>")


def plot_dialog(driver1, driver2, year, race, qualification1, qualification2):
    fig_speed_telemetry_plot, fig_speed_along_track_plot, fig_lap_plot = (
        run_in_parallel(
            [speed_telemetry_plot, speed_along_track_plot, lap_plot],
            driver1,
            driver2,
            year,
            race,
            qualification1,
            qualification2,
        )
    )
    return fig_speed_telemetry_plot, fig_speed_along_track_plot, fig_lap_plot


def calling_dialog_function(fig1, fig2, fig3):
    # print(f"inside calling dialog 1 {st.session_state.button_clicked}")
    # st.session_state.button_clicked = "A"
    dialog_function(fig1, fig2, fig3)
    # print(f"inside calling dialog 2 {st.session_state.button_clicked}")
    # st.session_state.button_clicked = False
