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


def find_faster_slower_df(df1, df2):
    len1, len2 = df1.shape[0], df2.shape[0]
    time1, time2 = max(df1["time"]), max(df2["time"])
    if len1 >= len2 and time1 < time2:
        time_diff_interval = int((time2 - time1) * 1000 / 250)
        drop_indices = np.linspace(
            10, len(df1) - 15, num=time_diff_interval + len1 - len2, dtype=int
        )
        df1 = df1.drop(drop_indices).reset_index(drop=True)
        return df1, df2
    elif len1 < len2 and time1 < time2:
        time_diff_interval = int((time2 - time1) * 1000 / 250)
        if (len2 - len1) < time_diff_interval:
            drop_indices = np.linspace(
                30, len(df1) - 50, num=time_diff_interval - (len2 - len1), dtype=int
            )
            df1 = df1.drop(drop_indices).reset_index(drop=True)
        return df1, df2
    elif len1 <= len2 and time1 > time2:
        time_diff_interval = int((time1 - time2) * 1000 / 250)
        drop_indices = np.linspace(
            10, len(df2) - 15, num=time_diff_interval + len2 - len1, dtype=int
        )
        df2 = df2.drop(drop_indices).reset_index(drop=True)
        return df2, df1
    elif len1 > len2 and time1 > time2:
        time_diff_interval = int((time1 - time2) * 1000 / 250)
        if (len1 - len2) < time_diff_interval:
            drop_indices = np.linspace(
                30, len(df2) - 50, num=time_diff_interval - (len1 - len2), dtype=int
            )
            df2 = df2.drop(drop_indices).reset_index(drop=True)
        return df2, df1
    else:
        return df1, df2


def lap_plot(d1, d2, year, race, q1, q2):

    cursor = connection()

    pos_data1 = cursor.execute(
        f"""select x,y, timeinsec, Abbreviation, TeamColor, qualification_session from pos_data_{year} where RaceName = '{race}' and FullName = '{d1}' and qualification_session = '{q1}' """
    ).fetchall()
    pos_data2 = cursor.execute(
        f"""select x,y, timeinsec, Abbreviation, TeamColor, qualification_session from pos_data_{year} where RaceName = '{race}' and FullName = '{d2}' and qualification_session = '{q2}' """
    ).fetchall()

    df1 = pd.DataFrame(
        pos_data1, columns=["x", "y", "time", "abbreviation", "color", "q"]
    )
    df2 = pd.DataFrame(
        pos_data2, columns=["x", "y", "time", "abbreviation", "color", "q"]
    )
    cursor.close()
    faster_df, slower_df = find_faster_slower_df(df1, df2)

    faster_color = f"#{faster_df.loc[0,'color']}"
    slower_color = f"#{slower_df.loc[0,'color']}"
    faster_color, slower_color = adjust_color_if_needed(faster_color, slower_color)
    faster_name = f"{faster_df.loc[0,'abbreviation']}"
    slower_name = f"{slower_df.loc[0,'abbreviation']}"
    faster_q = f"{faster_df.loc[0,'q']}"
    slower_q = f"{slower_df.loc[0,'q']}"
    faster_time = max(faster_df["time"])
    slower_time = max(slower_df["time"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=slower_df["x"],
            y=slower_df["y"],
            mode="lines",
            name=f"{slower_name} {slower_q} Path",
            line=dict(color=f"{slower_color}", shape="spline", dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=faster_df["x"],
            y=faster_df["y"],
            mode="lines",
            name=f"{faster_name} {faster_q} Path",
            line=dict(color=f"{faster_color}", shape="spline", dash="dash", width=5),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[slower_df["x"][0]],
            y=[slower_df["y"][0]],
            mode="markers",
            marker=dict(size=10, color=f"{slower_color}"),
            name=f"{slower_name} {slower_q}",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[faster_df["x"][0]],
            y=[faster_df["y"][0]],
            mode="markers",
            marker=dict(size=15, color=f"{faster_color}"),
            name=f"{faster_name} {faster_q}",
        )
    )

    # Define frames for both animations
    frames = []
    for i in range(max(len(faster_df), len(slower_df))):
        frame_data = []
        if i < len(slower_df):
            frame_data.extend(
                [
                    go.Scatter(
                        x=slower_df["x"][: i + 1],
                        y=slower_df["y"][: i + 1],
                        name=f"{slower_name} {slower_q} Path",
                        mode="lines",
                        line=dict(color=f"{slower_color}", shape="spline", dash="dash"),
                    ),
                    go.Scatter(
                        x=[slower_df["x"][i]],
                        y=[slower_df["y"][i]],
                        name=f"{slower_name} {slower_q}",
                        mode="markers",
                        marker=dict(size=10, color=f"{slower_color}"),
                    ),
                ]
            )
        if i < len(faster_df):
            frame_data.extend(
                [
                    go.Scatter(
                        x=faster_df["x"][: i + 1],
                        y=faster_df["y"][: i + 1],
                        name=f"{faster_name} {faster_q} Path",
                        mode="lines",
                        line=dict(
                            color=f"{faster_color}",
                            shape="spline",
                            dash="dash",
                            width=5,
                        ),
                    ),
                    go.Scatter(
                        x=[faster_df["x"][i]],
                        y=[faster_df["y"][i]],
                        name=f"{faster_name} {faster_q}",
                        mode="markers",
                        marker=dict(size=15, color=f"{faster_color}"),
                    ),
                ]
            )

        frames.append(go.Frame(data=frame_data, name=str(i)))

    fig.frames = frames

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=100, redraw=True),
                                transition=dict(duration=100),
                                fromcurrent=True,
                            ),
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False), mode="immediate"
                            ),
                        ],
                    ),
                ],
            )
        ],
        title=f"Lap Run",
        width=1000,
        height=600,
        template="plotly_white",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        legend=dict(
            x=1.02,
            y=0.5,
            xanchor="left",
            yanchor="middle",
        ),
    )
    fig.update_layout(
        xaxis=dict(
            range=[min(faster_df["x"]) - 100, max(faster_df["x"])]
        ),  # Adjust range based on data
        yaxis=dict(range=[min(faster_df["y"]) - 500, max(faster_df["y"]) + 500]),
    )

    # fig.update_xaxes(showticklabels=False, showgrid=True)
    # fig.update_yaxes(showticklabels=False, showgrid=True)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0,
        y=0.1,
        text=f"{faster_name}: Finished {faster_q} in {faster_time} Seconds<br>{slower_name}: Finished {slower_q} in {slower_time} seconds",
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
