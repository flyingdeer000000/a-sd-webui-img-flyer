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


def color_string_to_tuple(color_string):
    if color_string is None or len(color_string) == 0:
        return 0, 0, 0, 0

    color_values = color_string.strip().split(",")
    color_values = [int(value) for value in color_values]

    if len(color_values) == 3:
        # RGB color string
        return color_values[0], color_values[1], color_values[2], 255
    elif len(color_values) == 4:
        # RGBA color string
        return tuple(color_values)
    else:
        raise ValueError("Invalid color string format.")

