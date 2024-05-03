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



