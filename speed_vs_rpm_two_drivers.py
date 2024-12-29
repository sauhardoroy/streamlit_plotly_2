import sqlite3 as s3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import adjust_color_if_needed, connection, get_corner_info, normalize_string


def speed_vs_rpm_plot(d1, d2, year, race, q1, q2, gear):

    cursor = connection(f"{normalize_string(race.replace(' ','_'))}_{year}")
    print(gear)
    pos_data = cursor.execute(
        f"select *  from car_data where year = {year} and RaceName = '{race}' and ((FullName = '{d1}' and qualification_session = '{q1}') or  (FullName = '{d2}' and qualification_session = '{q2}')) "
    ).fetchall()

    columns = [desc[0] for desc in cursor.description]

    pos_data = pd.DataFrame(pos_data, columns=columns)

    gear_options = [
        {"label": str(gear), "value": gear} for gear in pos_data["nGear"].unique()
    ]

    d1_colour = f'#{pos_data[pos_data["FullName"] == d1]["TeamColor"].iloc[0]}'
    d2_colour = f'#{pos_data[pos_data["FullName"] == d2]["TeamColor"].iloc[0]}'
    d1_colour, d2_colour = adjust_color_if_needed(d1_colour, d2_colour)

    d1_abb = pos_data[pos_data["FullName"] == d1]["Abbreviation"].iloc[0]
    d2_abb = pos_data[pos_data["FullName"] == d2]["Abbreviation"].iloc[0]
    color_dict = {d1_abb: d1_colour, d2_abb: d2_colour}

    driver1_data = pos_data[(pos_data["FullName"] == d1)].rename(
        columns={"Abbreviation": "Name", "nGear": "Gear"}
    )
    driver2_data = pos_data[(pos_data["FullName"] == d2)].rename(
        columns={"Abbreviation": "Name", "nGear": "Gear"}
    )
    # print(driver1_data)
    if gear:
        driver1_data = driver1_data[driver1_data["Gear"].isin(gear)]
        driver2_data = driver2_data[driver2_data["Gear"].isin(gear)]
    fig = px.scatter(
        pd.concat([driver1_data, driver2_data]),
        x="RPM",
        y="Speed",
        opacity=1,
        color="Name",
        labels={"x": "RPM", "y": "Speed"},
        title="Speed vs RPM Scatter Plot",
        hover_data=["Gear"],
        color_discrete_map=color_dict,
    )
    fig.update_layout(
        title="Speed VS RPM",
        # showlegend=True,
        template="plotly_white",
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Below the chart
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        autosize=False,
        width=1000,  # Width for 5:3 ratio
        height=600,  # Height for 5:3 ratio
    )

    return fig
