import sqlite3 as s3

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils import adjust_color_if_needed, connection, get_corner_info, normalize_string


def speed_telemetry_plot(d1, d2, year, race, q1, q2):
    cursor = connection(f"race_info_{year}")

    driver_name = cursor.execute(
        f"select DriverNumber,FullName  from qualification_results where year = {year} and RaceName = '{race}' and FullName = '{d1}' "
    ).fetchall()

    columns = [desc[0] for desc in cursor.description]
    drivers_df = pd.DataFrame(driver_name, columns=columns)
    driver_name = cursor.execute(
        f"select DriverNumber,FullName  from qualification_results where year = {year} and RaceName = '{race}' and FullName = '{d2}' "
    ).fetchall()

    columns = [desc[0] for desc in cursor.description]

    drivers_df = pd.concat(
        [drivers_df, pd.DataFrame(driver_name, columns=columns)]
    ).reset_index()
    cursor.close()
    cursor = connection(f"{normalize_string(race.replace(' ','_'))}_{year}")
    distance_min, distance_max = (
        0,
        cursor.execute(
            f"select max(distance) from car_data where RaceName = '{race}' group by racename"
        ).fetchall()[0][0],
    )

    data = {
        "laps_driver": [],
        "telemetry_driver": [],
        "team_driver": [],
        "actions_driver": [],
        "avg_speed_driver": [],
    }
    qualification_list = [q1, q2]
    for index, dri_det in drivers_df.iterrows():

        driver_number = dri_det["DriverNumber"]
        # print(driver_number)
        telemetry_data = cursor.execute(
            f"select *  from car_data where racename= '{race}' and DriverNumber = '{driver_number}' and qualification_session = '{qualification_list[index]}' "
        ).fetchall()

        columns = [desc[0] for desc in cursor.description]
        telemetry_df = pd.DataFrame(telemetry_data, columns=columns)
        data["telemetry_driver"].append(telemetry_df)
        # print(data)
        data["team_driver"].append(telemetry_df.loc[0, "TeamName"])

        data["telemetry_driver"][index].loc[
            data["telemetry_driver"][index]["Brake"] > 0, "CurrentAction"
        ] = "Brake"
        data["telemetry_driver"][index].loc[
            data["telemetry_driver"][index]["Throttle"] >= 99, "CurrentAction"
        ] = "Full Throttle"
        data["telemetry_driver"][index].loc[
            (data["telemetry_driver"][index]["Brake"] == 0)
            & (data["telemetry_driver"][index]["Throttle"] < 99),
            "CurrentAction",
        ] = "Cornering"

        data["telemetry_driver"][index]["ActionID"] = (
            data["telemetry_driver"][index]["CurrentAction"]
            != data["telemetry_driver"][index]["CurrentAction"].shift(1)
        ).cumsum()

        data["actions_driver"].append(
            data["telemetry_driver"][index][["ActionID", "CurrentAction", "Distance"]]
            .groupby(["ActionID", "CurrentAction"])
            .max("Distance")
            .reset_index()
        )

        data["actions_driver"][index]["Driver"] = dri_det["FullName"]

        data["actions_driver"][index]["DistanceDelta"] = data["actions_driver"][index][
            "Distance"
        ] - data["actions_driver"][index]["Distance"].shift(1)
        data["actions_driver"][index].loc[0, "DistanceDelta"] = data["actions_driver"][
            index
        ].loc[0, "Distance"]

        data["avg_speed_driver"].append(
            np.mean(
                data["telemetry_driver"][index]["Speed"].loc[
                    (data["telemetry_driver"][index]["Distance"] >= distance_min)
                    & (data["telemetry_driver"][index]["Distance"] <= distance_max)
                ]
            )
        )

    cursor.close()

    if data["avg_speed_driver"][0] > data["avg_speed_driver"][1]:
        speed_text = f"{qualification_list[0]} {drivers_df['FullName'][0]} faster by {round(data['avg_speed_driver'][0] - data['avg_speed_driver'][1],2)} km/h on average"
    else:
        speed_text = f"{qualification_list[1]} {drivers_df['FullName'][1]} faster by {round(data['avg_speed_driver'][1] - data['avg_speed_driver'][0],2)} km/h on average"

    all_actions = pd.concat(
        [
            pd.DataFrame(data["actions_driver"][0]),
            pd.DataFrame(data["actions_driver"][1]),
        ]
    )

    driver1 = normalize_string(drivers_df["FullName"][0])
    driver2 = normalize_string(drivers_df["FullName"][1])

    distance_min = 0
    distance_max = distance_max
    # speed_text = "Speed Comparison"

    corner_info = get_corner_info(race, year)
    telemetry_colors = {
        "Full Throttle": "green",
        "Cornering": "grey",
        "Brake": "red",
    }

    # Plotly figure
    fig = go.Figure()

    d1_colour = f'#{data["telemetry_driver"][0]["TeamColor"][0]}'
    d2_colour = f'#{data["telemetry_driver"][1]["TeamColor"][0]}'
    adjust_color_if_needed
    d1_colour, d2_colour = adjust_color_if_needed(d1_colour, d2_colour)
    color_scale = [
        d1_colour,
        d2_colour,
    ]
    # Lineplot for Speed
    fig.add_trace(
        go.Scatter(
            x=data["telemetry_driver"][0]["Distance"],
            y=data["telemetry_driver"][0]["Speed"],
            mode="lines",
            name=f"{driver1} {q1}",
            line=dict(color=color_scale[0]),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data["telemetry_driver"][1]["Distance"],
            y=data["telemetry_driver"][1]["Speed"],
            mode="lines",
            name=f"{driver2} {q2}",
            line=dict(color=color_scale[1]),
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

    fig.update_layout(
        title="Speed Over Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (kmph)",
        barmode="overlay",  # ['stack', 'group', 'overlay', 'relative']
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        width=1000,
        height=600,
        template="plotly_white",
    )

    # Highlight Speed Difference
    # fig.add_annotation(
    #     x=distance_min + 15, y=200, text=speed_text, showarrow=False, font=dict(size=15)
    # )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=0.1,  # Moved upwards
        text=f"{speed_text}",
        showarrow=False,
        align="left",
        font=dict(size=12),
        bordercolor="White",
        borderwidth=1,
        borderpad=4,
        # bgcolor="white",
        opacity=1,
    )
    # Zoom in on the specific part
    fig.update_xaxes(range=[distance_min, distance_max])
    return fig
