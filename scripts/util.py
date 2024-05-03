import glob
import os


def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def file_count(target, suffix="*.png"):
    pattern = os.path.join(target, suffix)
    files = glob.glob(pattern)
    return len(files)


def str_exist(s):
    s = s.strip()
    return s is not None and len(s) > 0


def color_string_to_tuple(c_str):
    r = 0
    g = 0
    b = 0
    a = 0
    if c_str is None or len(c_str) == 0:
        return a, g, b, a

    c_str = c_str.lower()

    if c_str[0] == '#':
        if len(c_str) >= 7:
            r = int(c_str[1:3], 16)  # Extract and convert the red component
            g = int(c_str[3:5], 16)  # Extract and convert the green component
            b = int(c_str[5:7], 16)  # Extract and convert the blue component

        if len(c_str) >= 9:
            a = int(c_str[7:9], 16)  # Extract and convert the alpha component
        else:
            a = 255
        return r, g, b, a

    if c_str[0] == 'r':
        c_str = (c_str
                 .replace('rgba', '').replace('rgb', '')
                 .replace('(', '').replace(')', ''))

    color_values = c_str.strip().split(",")
    color_values = [int(value) for value in color_values]

    if len(color_values) < 3:
        raise ValueError(f"Invalid color string: {c_str}")

    if len(color_values) >= 3:
        r, b, g = color_values[0], color_values[1], color_values[2]
        a = 255

    if len(color_values) >= 4:
        a = color_values[3]

    return r, g, b, a
