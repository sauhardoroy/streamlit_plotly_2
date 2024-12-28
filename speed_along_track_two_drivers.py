import sqlite3 as s3

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils import (
    adjust_color_if_needed,
    connection,
    hex_check_convert,
    normalize_string,
)


def speed_along_track_plot(d1, d2, year, race, q1, q2):

    cursor = connection()
    telemetry_data = cursor.execute(
        f"""select *  from telemetry_data_{year} 
            where year = {year} and RaceName = '{race}' 
            and ((FullName = '{d1}' and qualification_session = '{q1}') 
            or (FullName = '{d2}' and qualification_session = '{q2}')) """
    ).fetchall()

    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    telemetry_data = pd.DataFrame(telemetry_data, columns=columns)
    distance_min, distance_max = (0, max(telemetry_data["Distance"]))

    num_minisectors = 25

    # Grab the maximum value of distance that is known in the telemetry
    total_distance = distance_max

    # Generate equally sized mini-sectors
    minisector_length = total_distance / num_minisectors

    # Initiate minisector variable, with 0 (meters) as a starting point.
    minisectors = [0]

    # Add multiples of minisector_length to the minisectors
    for i in range(0, (num_minisectors - 1)):
        minisectors.append(minisector_length * (i + 1))

    telemetry_data["Minisector"] = telemetry_data["Distance"].apply(
        lambda dist: (int((dist // minisector_length) + 1))
    )
    # print(f"""1 \n {telemetry_data}""")
    average_speed = (
        telemetry_data.groupby(["Minisector", "FullName", "qualification_session"])[
            "Speed"
        ]
        .mean()
        .reset_index()
    )
    # print(f"""2 \n {average_speed}""")
    # Select the driver with the highest average speed
    fastest_driver = average_speed.loc[
        average_speed.groupby(["Minisector"])["Speed"].idxmax()
    ]
    # print(f"""3 \n {fastest_driver}""")

    fastest_driver = fastest_driver[
        ["Minisector", "FullName", "qualification_session"]
    ].rename(
        columns={
            "FullName": "Fastest_driver",
            "qualification_session": "fastest_qualification_session",
        }
    )

    # Join the fastest driver per minisector with the full telemetry
    telemetry_data = telemetry_data.merge(fastest_driver, on=["Minisector"])

    # Order the data by distance to make matploblib does not get confused
    telemetry_data = telemetry_data.sort_values(by=["Distance"])
    # print(
    #     f"""4 \n {telemetry_data[['Minisector','FullName','fastest_qualification_session','Distance']]}"""
    # )
    # Convert driver name to integer
    telemetry_data.loc[
        (telemetry_data["Fastest_driver"] == d1)
        & (telemetry_data["fastest_qualification_session"] == q1),
        "Fastest_driver_int",
    ] = 1
    telemetry_data.loc[
        (telemetry_data["Fastest_driver"] == d2)
        & (telemetry_data["fastest_qualification_session"] == q2),
        "Fastest_driver_int",
    ] = 2
    # print(
    #     f"telemetry with faster dirver int {telemetry_data[['Minisector','FullName','fastest_qualification_session','Distance']]}"
    # )
    # Prepare data
    x = np.array(telemetry_data["X"].values)
    y = np.array(telemetry_data["Y"].values)
    fastest_driver_array = telemetry_data["Fastest_driver_int"].to_numpy().astype(float)
    # print("ran till 5")
    pc_driver1 = round(
        telemetry_data[
            (telemetry_data["Fastest_driver"] == d1)
            & (telemetry_data["fastest_qualification_session"] == q1)
        ].shape[0]
        * 100
        / telemetry_data.shape[0]
    )
    pc_driver2 = round(
        telemetry_data[
            (telemetry_data["Fastest_driver"] == d2)
            & (telemetry_data["fastest_qualification_session"] == q2)
        ].shape[0]
        * 100
        / telemetry_data.shape[0]
    )
    # Add a widget in the bottom left corner to show the percentage of time each driver was fastest
    # print(f""" pc_driver1 {pc_driver1}""")
    # Generate line segments
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create the color mapping
    d1_colour = (
        f'#{telemetry_data[telemetry_data["FullName"] == d1]["TeamColor"].iloc[0]}'
    )
    d2_colour = (
        f'#{telemetry_data[telemetry_data["FullName"] == d2]["TeamColor"].iloc[0]}'
    )
    # print("ran till 6")
    d1_colour, d2_colour = adjust_color_if_needed(d1_colour, d2_colour)
    # print(f"Adjusted colors: {d1_colour}, {d2_colour}")
    color_scale = [d1_colour, d2_colour]
    # print(f"color scale {color_scale}")
    driver1 = normalize_string(d1)
    driver2 = normalize_string(d2)
    custom_tick_labels = [f"{driver1} {q1}", f"{driver2} {q2}"]
    # print(f"fastest driver array{fastest_driver_array}")
    color_mapping = np.vectorize(lambda x: color_scale[int(x) - 1])(
        fastest_driver_array
    ).tolist()

    fig = go.Figure()

    # Add the line trace with color mapping
    for i in range(len(segments)):
        fig.add_trace(
            go.Scatter(
                x=[segments[i, 0, 0], segments[i, 1, 0]],
                y=[segments[i, 0, 1], segments[i, 1, 1]],
                mode="lines",
                line=dict(
                    color=color_mapping[i],
                    width=5,
                ),
                hoverinfo="text",
                text=f"Driver: {custom_tick_labels[int(fastest_driver_array[i]) - 1]}",
                showlegend=False,
            )
        )

    # Add custom legend
    for driver, color in zip(custom_tick_labels, color_scale):
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color=color),
                legendgroup=driver,
                showlegend=True,
                name=driver,
            )
        )

    fig.update_layout(
        title=f"Speed Over Track",
        # margin=dict(l=20, r=50, t=30, b=20),
        showlegend=True,
        xaxis=dict(scaleanchor="y", scaleratio=1),  # Equal scaling
        width=1000,
        height=600,
        template="plotly_white",
        legend=dict(
            x=1,
            y=0.5,
            xanchor="left",
            yanchor="middle",
        ),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=0.1,
        text=f"{d1}: {pc_driver1}%<br>{d2}: {pc_driver2}%",
        showarrow=False,
        align="left",
        font=dict(size=12),
        bordercolor="White",
        borderwidth=1,
        borderpad=4,
        # bgcolor="white",
        opacity=1,
    )

    return fig
