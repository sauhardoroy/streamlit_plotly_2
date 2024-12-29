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

    cursor = connection(f"{normalize_string(race.replace(' ','_'))}_{year}")
    telemetry_data = cursor.execute(
        f"""select *  from telemetry_data 
            where year = {year} and RaceName = '{race}' 
            and ((FullName = '{d1}' and qualification_session = '{q1}') 
            or (FullName = '{d2}' and qualification_session = '{q2}')) """
    ).fetchall()

    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    telemetry_data = pd.DataFrame(telemetry_data, columns=columns)
    distance_min, distance_max = (0, max(telemetry_data["Distance"]))

    num_minisectors = 25

    total_distance = distance_max

    minisector_length = total_distance / num_minisectors

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

    fastest_driver = average_speed.loc[
        average_speed.groupby(["Minisector"])["Speed"].idxmax()
    ]

    fastest_driver = fastest_driver[
        ["Minisector", "FullName", "qualification_session"]
    ].rename(
        columns={
            "FullName": "Fastest_driver",
            "qualification_session": "fastest_qualification_session",
        }
    )

    telemetry_data = telemetry_data.merge(fastest_driver, on=["Minisector"])

    telemetry_data = telemetry_data.sort_values(by=["Distance"])

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

    x = np.array(telemetry_data["X"].values)
    y = np.array(telemetry_data["Y"].values)
    fastest_driver_array = telemetry_data["Fastest_driver_int"].to_numpy().astype(float)

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

    points = np.array([x, y]).T.reshape(-1, 1, 2)

    d1_colour = (
        f'#{telemetry_data[telemetry_data["FullName"] == d1]["TeamColor"].iloc[0]}'
    )
    d2_colour = (
        f'#{telemetry_data[telemetry_data["FullName"] == d2]["TeamColor"].iloc[0]}'
    )

    d1_colour, d2_colour = adjust_color_if_needed(d1_colour, d2_colour)

    color_map = {1: d1_colour, 2: d2_colour}

    data = (
        telemetry_data[
            [
                "X",
                "Y",
                "Distance",
                "Fastest_driver",
                "fastest_qualification_session",
                "Fastest_driver_int",
            ]
        ]
        .apply(lambda row: tuple(row), axis=1)
        .tolist()
    )

    driver1 = normalize_string(d1)
    driver2 = normalize_string(d2)
    custom_tick_labels = [f"{driver1} {q1}", f"{driver2} {q2}"]

    fig = go.Figure()
    custom_tick_labels = [f"{d1} {q1}", f"{d2} {q2}"]
    fastest_driver_array = telemetry_data["Fastest_driver_int"].to_numpy().astype(float)

    for i in range(len(data) - 1):
        x_values = [data[i][0], data[i + 1][0]]
        y_values = [data[i][1], data[i + 1][1]]
        line_color = color_map[int(data[i][5])]

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                line=dict(color=line_color, width=3),
                hoverinfo="text",
                text=f"Driver: {custom_tick_labels[int(fastest_driver_array[i]) - 1]}",
                showlegend=False,
            )
        )
    for driver, color in zip(custom_tick_labels, color_map.values()):
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
    # Customize layout
    fig.update_layout(
        title="Speed Over Track",
        # showlegend=True,
        legend_title="Names",
        width=1000,
        height=600,
        template="plotly_white",
        xaxis=dict(scaleanchor="y", scaleratio=1),
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
        x=0.2,
        y=0.1,
        text=f"{q1} {d1}: {pc_driver1}%<br>{q2} {d2}: {pc_driver2}%",
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
