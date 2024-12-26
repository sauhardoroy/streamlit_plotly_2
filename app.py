import sqlite3 as s3

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from speed_analysis_two_drivers import load_session, plot_chart
from utils import get_corner_info, get_race_drivers

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
        all_actions, data, distance_max = plot_chart(driver1, driver2, year, race)
        with st.expander(label="Expand to see All Actions"):
            st.dataframe(all_actions)

        driver1 = driver1
        driver2 = driver2
        st.write(f"driver 1 is {driver1}")
        st.write(f"driver 2 is {driver2}")
        distance_min = 0
        distance_max = distance_max
        speed_text = "Speed Comparison"

        telemetry_colors = {
            "Full Throttle": "green",
            "Cornering": "grey",
            "Brake": "red",
        }

        # Plotly figure
        fig = go.Figure()
        st.write(data["telemetry_driver"][0])
        st.write(data["telemetry_driver"][1])
        # Lineplot for Speed
        fig.add_trace(
            go.Scatter(
                x=data["telemetry_driver"][0]["Distance"],
                y=data["telemetry_driver"][0]["Speed"],
                mode="lines",
                name=driver1,
                line=dict(color=f'#{data["telemetry_driver"][0]["TeamColor"][0]}'),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data["telemetry_driver"][1]["Distance"],
                y=data["telemetry_driver"][1]["Speed"],
                mode="lines",
                name=driver2,
                line=dict(color=f'#{data["telemetry_driver"][1]["TeamColor"][0]}'),
            )
        )
        for index, item in enumerate(corner_info):
            fig.add_vline(
                x=item[0],
                line_dash="dash",
                line_color="rgba(255, 255, 255, 0.5)",  # Off-white with 50% opacity
                annotation_text=f"C {index+1}",
                annotation_position=(
                    "top left" if index % 2 == 0 else "bottom left"
                ),  # Alternate positions
                annotation_font_size=10,  # Optional: Adjust font size for clarity
                opacity=0.5,  # Set line opacity to 50%
            )

        # # Horizontal Barplot for Telemetry
        # for driver in [driver1, driver2]:
        #     driver_actions = all_actions.loc[all_actions["Driver"] == driver]
        #     previous_action_end = 0
        #     for _, action in driver_actions.iterrows():
        #         fig.add_trace(
        #             go.Bar(
        #                 x=[action["DistanceDelta"]],
        #                 y=[driver],
        #                 orientation="h",
        #                 base=[previous_action_end],
        #                 marker=dict(color=telemetry_colors[action["CurrentAction"]]),
        #                 name=action["CurrentAction"],
        #             )
        #         )
        #         previous_action_end += action["DistanceDelta"]

        # Style adjustments
        fig.update_layout(
            title="F1 Telemetry: Speed Over Distance",
            xaxis_title="Distance (m)",
            yaxis_title="Speed (kmph)",
            barmode="relative",
            showlegend=True,
            legend_title="Telemetry Actions",
            legend=dict(
                orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5
            ),
            width=1000,
            height=600,
            template="plotly_white",
        )

        # Highlight Speed Difference
        # fig.add_annotation(
        #     x=distance_min + 15, y=200, text=speed_text, showarrow=False, font=dict(size=15)
        # )

        # Zoom in on the specific part
        fig.update_xaxes(range=[distance_min, distance_max])

        # Streamlit display
        st.title("Driver Telemetry Analysis")
        st.plotly_chart(fig, use_container_width=True)
