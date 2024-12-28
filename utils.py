import colorsys
import sqlite3 as s3
import threading
import unicodedata


def connection():
    conn = s3.connect("database.sqlite3", check_same_thread=False)
    cursor = conn.cursor()
    return cursor


def get_race_drivers():

    cursor = connection()

    # with st.form("Save periods"):
    race_with_drivers = cursor.execute("select * from race_with_drivers").fetchall()
    return race_with_drivers


def get_corner_info(race, year):

    cursor = connection()

    # with st.form("Save periods"):
    corner_info = cursor.execute(
        f"select distance from circuit_info where racename = '{race}' and year = {year}"
    ).fetchall()
    return corner_info


def hex_check_convert(value):
    if isinstance(value, str):
        return value if value.startswith("#") else f"#{value}"


def is_color_close(color1, color2, threshold=0.1):
    # Convert hex to RGB
    color1_rgb = tuple(int(color1[i : i + 2], 16) for i in (1, 3, 5))
    color2_rgb = tuple(int(color2[i : i + 2], 16) for i in (1, 3, 5))

    # Convert RGB to HSV
    color1_hsv = colorsys.rgb_to_hsv(*[x / 255.0 for x in color1_rgb])
    color2_hsv = colorsys.rgb_to_hsv(*[x / 255.0 for x in color2_rgb])

    # Compare hue values
    return abs(color1_hsv[0] - color2_hsv[0]) < threshold


def adjust_color_if_needed(color1, color2):
    if is_color_close(color1, color2):
        # Change color2 to a contrasting color (e.g., complementary color)
        color2_rgb = tuple(int(color2[i : i + 2], 16) for i in (1, 3, 5))
        color2_hsv = colorsys.rgb_to_hsv(*[x / 255.0 for x in color2_rgb])
        # Adjust hue by 180 degrees (0.5 in HSV space)
        new_hue = (color2_hsv[0] + 0.5) % 1.0
        new_color2_rgb = colorsys.hsv_to_rgb(new_hue, color2_hsv[1], color2_hsv[2])
        new_color2_hex = "#{:02x}{:02x}{:02x}".format(
            int(new_color2_rgb[0] * 255),
            int(new_color2_rgb[1] * 255),
            int(new_color2_rgb[2] * 255),
        )
        adjust_color_if_needed(color1, new_color2_hex)
        return color1, new_color2_hex
    return color1, color2


def thread_wrapper(func, args, result_holder, index):
    result_holder[index] = func(*args)


# Launch in parallel
def run_in_parallel(function_list, driver1, driver2, year, race, q1, q2):
    results = [None, None, None]  # To hold the results of the threads

    # Create threads
    thread1 = threading.Thread(
        target=thread_wrapper,
        args=(function_list[0], (driver1, driver2, year, race, q1, q2), results, 0),
    )
    thread2 = threading.Thread(
        target=thread_wrapper,
        args=(function_list[1], (driver1, driver2, year, race, q1, q2), results, 1),
    )
    thread3 = threading.Thread(
        target=thread_wrapper,
        args=(function_list[2], (driver1, driver2, year, race, q1, q2), results, 2),
    )

    # Start threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()
    thread3.join()

    return results


def normalize_string(value):

    normalized = unicodedata.normalize("NFKD", value)

    return "".join(c for c in normalized if not unicodedata.combining(c))
