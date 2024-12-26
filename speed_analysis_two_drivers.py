import sqlite3 as s3

# import fastf1 as ff1
import numpy as np
import pandas as pd

# from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure

# Enable the cache


def connection():
    conn = s3.connect("database.sqlite3", check_same_thread=False)
    cursor = conn.cursor()
    return cursor


def load_session(year, race):

    cursor = connection()

    # with st.form("Save periods"):
    race_events = cursor.execute(
        f"select * from race_events where year = '{year}' and EventName = '{race}' "
    ).fetchall()

    race_details = {
        "country": race_events[1],
        "location": race_events[2],
        "round": race_events[0],
        "date": race_events[3],
        "name": race_events[4],
    }
    cursor.close()
    return race_details


def plot_chart(
    d1,
    d2,
    year,
    race,
):
    # print(d1)
    # session.results
    cursor = connection()

    # with st.form("Save periods"):
    driver_name = cursor.execute(
        f"select DriverNumber,FullName  from qualification_results where year = {year} and RaceName = '{race}' and FullName = '{d1}' "
    ).fetchall()
    # print(driver_name)
    columns = [desc[0] for desc in cursor.description]
    drivers_df = pd.DataFrame(driver_name, columns=columns)
    driver_name = cursor.execute(
        f"select DriverNumber,FullName  from qualification_results where year = {year} and RaceName = '{race}' and FullName = '{d2}' "
    ).fetchall()
    # print(driver_name)
    columns = [desc[0] for desc in cursor.description]
    # print(columns)
    # Convert to DataFrame
    drivers_df = pd.concat(
        [drivers_df, pd.DataFrame(driver_name, columns=columns)]
    ).reset_index()
    # print(drivers_df)
    distance_min, distance_max = (
        0,
        cursor.execute(
            f"select max(distance) from car_data_{year} where RaceName = '{race}' group by racename"
        ).fetchall()[0][0],
    )

    data = {
        "laps_driver": [],
        "telemetry_driver": [],
        "team_driver": [],
        "actions_driver": [],
        "avg_speed_driver": [],
    }
    for index, dri_det in drivers_df.iterrows():
        # Extracting the laps
        # data["laps_driver"].append(session.laps.pick_drivers(dri_det["DriverNumber"]))
        driver_number = dri_det["DriverNumber"]
        print(driver_number)
        telemetry_data = cursor.execute(
            f"select *  from car_data_{year} where racename= '{race}' and DriverNumber = '{driver_number}' "
        ).fetchall()

        columns = [desc[0] for desc in cursor.description]
        telemetry_df = pd.DataFrame(telemetry_data, columns=columns)
        # print("printing telemetry df")
        # print(telemetry_df)
        data["telemetry_driver"].append(telemetry_df)
        print(data)
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

        # Numbering each unique action to identify changes, so that we can group later on
        data["telemetry_driver"][index]["ActionID"] = (
            data["telemetry_driver"][index]["CurrentAction"]
            != data["telemetry_driver"][index]["CurrentAction"].shift(1)
        ).cumsum()

        # Identifying all unique actions
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

    if data["avg_speed_driver"][0] > data["avg_speed_driver"][1]:
        speed_text = f"{drivers_df['FullName'][0]} {round(data['avg_speed_driver'][0] - data['avg_speed_driver'][1],2)} km/h faster"
    else:
        speed_text = f"{drivers_df['FullName'][1]} {round(data['avg_speed_driver'][1] - data['avg_speed_driver'][0],2)} km/h faster"

    all_actions = pd.concat(
        [
            pd.DataFrame(data["actions_driver"][0]),
            pd.DataFrame(data["actions_driver"][1]),
        ]
    )

    driver1 = drivers_df["FullName"][0]
    driver2 = drivers_df["FullName"][1]

    plt.rcParams["figure.figsize"] = [13, 6]
    plt.rcParams["figure.autolayout"] = True

    telemetry_colors = {
        "Full Throttle": "green",
        "Cornering": "grey",
        "Brake": "red",
    }

    fig, ax = plt.subplots(2)

    ##############################
    #
    # Lineplot for speed
    #
    ##############################
    ax[0].plot(
        data["telemetry_driver"][0]["Distance"],
        data["telemetry_driver"][0]["Speed"],
        label=driver1,
        # color=ff1.plotting.team_color(data["team_driver"][0]),
    )
    ax[0].plot(
        data["telemetry_driver"][1]["Distance"],
        data["telemetry_driver"][1]["Speed"],
        label=driver2,
        # color=ff1.plotting.team_color(data["team_driver"][1]),
    )

    # Speed difference
    ax[0].text(distance_min + 15, 200, speed_text, fontsize=15)

    ax[0].set(ylabel="Speed")
    ax[0].legend(loc="lower right")

    ##############################
    #
    # Horizontal barplot for telemetry
    #
    ##############################
    for driver in [driver1, driver2]:
        driver_actions = all_actions.loc[all_actions["Driver"] == driver]

        previous_action_end = 0
        for _, action in driver_actions.iterrows():
            ax[1].barh(
                [driver],
                action["DistanceDelta"],
                left=previous_action_end,
                color=telemetry_colors[action["CurrentAction"]],
            )

            previous_action_end = previous_action_end + action["DistanceDelta"]

    ##############################
    #
    # Styling of the plot
    #
    ##############################
    # Set x-label
    plt.xlabel("Distance")

    # Invert y-axis
    plt.gca().invert_yaxis()

    # Remove frame from plot
    ax[1].spines["top"].set_visible(False)
    ax[1].spines["right"].set_visible(False)
    ax[1].spines["left"].set_visible(False)

    # Add legend
    labels = list(telemetry_colors.keys())
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=telemetry_colors[label]) for label in labels
    ]
    ax[1].legend(handles, labels)

    # Zoom in on the specific part we want to see
    ax[0].set_xlim(distance_min, distance_max)
    ax[1].set_xlim(distance_min, distance_max)

    # Save the plot
    plt.savefig("abcsda.png", dpi=300)
    # plt.savefig(
    #     f'{race_details["country"]}_{race_details["name"]}_{race_details["round"]}_{driver1}_{driver2}.png',
    #     dpi=300,
    # )
    return all_actions, data, distance_max


# if __name__ == "main":

#     all_actions, data, distance_max = plot_chart(
#         "Max Verstappen", "Lando Norris", 2024, "Bahrain Grand Prix"
#     )
#     print(all_actions)
#     print(data)
