import sqlite3 as s3

import pandas as pd
import streamlit as st
from lap_run_two_drivers import lap_plot
from speed_along_track_two_drivers import speed_along_track_plot
from speed_analysis_two_drivers import speed_telemetry_plot
from speed_vs_rpm_two_drivers import speed_vs_rpm_plot
from utils import run_in_parallel


@st.dialog("Data Viz", width="large")
def dialog_function(fig1, fig2, fig3, fig4):

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
    try:
        options = st.multiselect("Select Gears", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        if options:
            st.plotly_chart(
                speed_vs_rpm_plot(
                    st.session_state.driver1,
                    st.session_state.driver2,
                    st.session_state.year,
                    st.session_state.race,
                    st.session_state.qualification1,
                    st.session_state.qualification2,
                    options,
                ),
                use_container_width=True,
            )
        else:
            st.plotly_chart(fig4, use_container_width=True)
        # st.markdown(fig4, unsafe_allow_html=True)
        # st.html(fig4)
    except Exception as e:
        st.error(f"An error occurred while generating the plots: {e}")

    st.html("</span>")


def plot_dialog(driver1, driver2, year, race, qualification1, qualification2, gears):
    (
        fig_speed_telemetry_plot,
        fig_speed_along_track_plot,
        fig_lap_plot,
        fig_speed_vs_rpm,
    ) = run_in_parallel(
        [speed_telemetry_plot, speed_along_track_plot, lap_plot, speed_vs_rpm_plot],
        driver1,
        driver2,
        year,
        race,
        qualification1,
        qualification2,
        gears,
    )
    return (
        fig_speed_telemetry_plot,
        fig_speed_along_track_plot,
        fig_lap_plot,
        fig_speed_vs_rpm,
    )


def calling_dialog_function(fig1, fig2, fig3, fig4):
    # print(f"inside calling dialog 1 {st.session_state.button_clicked}")
    # st.session_state.button_clicked = "A"
    dialog_function(fig1, fig2, fig3, fig4)
    # print(f"inside calling dialog 2 {st.session_state.button_clicked}")
    # st.session_state.button_clicked = False
