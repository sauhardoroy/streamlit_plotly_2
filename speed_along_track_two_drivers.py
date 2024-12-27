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


def speed_along_track_plot(d1, d2, year, race):

    cursor = connection()
    telemetry_data = cursor.execute(
        f"select *  from car_telemetry_{year} where year = {year} and RaceName = '{race}' and FullName in ('{d1}', '{d2}') "
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

    average_speed = (
        telemetry_data.groupby(["Minisector", "FullName"])["Speed"].mean().reset_index()
    )

    # Select the driver with the highest average speed
    fastest_driver = average_speed.loc[
        average_speed.groupby(["Minisector"])["Speed"].idxmax()
    ]
    # fastest_driver
    # Get rid of the speed column and rename the driver column
    fastest_driver = fastest_driver[["Minisector", "FullName"]].rename(
        columns={"FullName": "Fastest_driver"}
    )

    # Join the fastest driver per minisector with the full telemetry
    telemetry_data = telemetry_data.merge(fastest_driver, on=["Minisector"])

    # Order the data by distance to make matploblib does not get confused
    telemetry_data = telemetry_data.sort_values(by=["Distance"])

    # Convert driver name to integer
    telemetry_data.loc[telemetry_data["Fastest_driver"] == d1, "Fastest_driver_int"] = 1
    telemetry_data.loc[telemetry_data["Fastest_driver"] == d2, "Fastest_driver_int"] = 2

    # Prepare data
    x = np.array(telemetry_data["X"].values)
    y = np.array(telemetry_data["Y"].values)
    fastest_driver_array = telemetry_data["Fastest_driver_int"].to_numpy().astype(float)

    # Generate line segments
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create the color mapping
    d1_colour = telemetry_data[telemetry_data["FullName"] == d1]["TeamColor"].iloc[0]
    d2_colour = telemetry_data[telemetry_data["FullName"] == d2]["TeamColor"].iloc[0]

    d1_colour, d2_colour = adjust_color_if_needed(d1_colour, d2_colour)
    print(f"Adjusted colors: {d1_colour}, {d2_colour}")
    color_scale = [
        hex_check_convert(d1_colour),
        hex_check_convert(d2_colour),
    ]
    driver1 = normalize_string(d1)
    driver2 = normalize_string(d2)
    custom_tick_labels = [f"{driver1}", f"{driver2}"]

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

    # Adjust axis settings
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
        showlegend=True,
        xaxis=dict(scaleanchor="y", scaleratio=1),  # Equal scaling
        title=f"Speed Over Track",
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

    return fig
