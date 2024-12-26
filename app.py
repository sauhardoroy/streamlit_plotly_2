import sqlite3 as s3

import plotly.graph_objects as go
import streamlit as st

# from speed_analysis_first_last_quali import load_session, plot_chart
from speed_analysis_two_drivers import load_session, plot_chart

st.header("Data Vis")
conn = s3.connect("database.sqlite3", check_same_thread=False)
cursor = conn.cursor()


# with st.form("Save periods"):
race_with_drivers = cursor.execute("select * from race_with_drivers").fetchall()

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
if "year" not in st.session_state:
    st.session_state.year = None

if "race" not in st.session_state:
    st.session_state.race = None

if "driver1" not in st.session_state:
    st.session_state.driver1 = None

if "driver2" not in st.session_state:
    st.session_state.driver2 = None

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

year = col1.selectbox(
    "select year",
    years_race_with_drivers,
    placeholder="Enter Race",
)


if year:
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
    if race:
        st.session_state.race = race
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
        if driver1:
            st.session_state.driver1 = driver1
            driver2_race_with_drivers_filtered = sorted(
                set(
                    [
                        race_with_drivers[item][5]
                        for item in range(len(race_with_drivers))
                        if race_with_drivers[item][3] == st.session_state.year
                        and race_with_drivers[item][2] == st.session_state.race
                        and race_with_drivers[item][5] != st.session_state.driver1
                    ]
                ),
                reverse=False,
            )
            driver2 = col4.selectbox(
                "select driver2",
                driver2_race_with_drivers_filtered,
            )
            if driver2:
                st.session_state.driver2 = driver2
if st.session_state.driver2 and st.session_state.driver1:
    all_actions, data, distance_max = plot_chart(driver1, driver2, year, race)
    with st.expander(label="Expand to see All Actions"):
        st.dataframe(all_actions)

# submitted = st.form_submit_button("plot")
# if submitted:
#     comment = "some comment"
#     a, b, c = 1, 2, 3
#     col1, col2, col3 = st.columns(3)
#     col1.metric("val", a)
#     col2.metric("val", b)
#     col3.metric("val", c)

import pandas as pd
import plotly.graph_objects as go

# Mocked data for demonstration
# Replace with actual data for `data`, `all_actions`, `driver1`, `driver2`, etc.


driver1 = st.session_state.driver1
driver2 = st.session_state.driver2
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

# Lineplot for Speed
fig.add_trace(
    go.Scatter(
        x=data["telemetry_driver"][0]["Distance"],
        y=data["telemetry_driver"][0]["Speed"],
        mode="lines",
        name=driver1,
        line=dict(color="red"),
    )
)

fig.add_trace(
    go.Scatter(
        x=data["telemetry_driver"][1]["Distance"],
        y=data["telemetry_driver"][1]["Speed"],
        mode="lines",
        name=driver2,
        line=dict(color="white"),
    )
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
    xaxis_title="Distance (m)",
    yaxis_title="Speed (kmph)",
    barmode="relative",
    showlegend=True,
    legend_title="Telemetry Actions",
    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
    width=1000,
    height=600,
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
