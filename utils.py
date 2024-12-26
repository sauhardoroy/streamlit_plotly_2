import sqlite3 as s3


def get_race_drivers():
    conn = s3.connect("database.sqlite3", check_same_thread=False)
    cursor = conn.cursor()

    # with st.form("Save periods"):
    race_with_drivers = cursor.execute("select * from race_with_drivers").fetchall()
    return race_with_drivers


def get_corner_info(race, year):

    conn = s3.connect("database.sqlite3", check_same_thread=False)
    cursor = conn.cursor()

    # with st.form("Save periods"):
    corner_info = cursor.execute(
        f"select distance from circuit_info where racename = '{race}' and year = {year}"
    ).fetchall()
    return corner_info
