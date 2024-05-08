import pathlib
import subprocess
import traceback


def fetch_by_yt_dlp(
        src_path,
        des_path,
        t_start,
        t_end,
        num_attempts=3,
        url_base="",
        quiet=False,
        force=True,
):
    des_path = des_path.strip()
    if len(des_path) == 0:
        des_path = "temp/track.wav"

    if not des_path.endswith(".wav"):
        des_path = des_path + ".wav"

    output_path = pathlib.Path(des_path)
    if output_path.exists():
        if not force:
            return output_path
        else:
            output_path.unlink()

    section_arg = ""
    if t_end > t_start:
        section_arg = f"""
            --download-sections "*{t_start}-{t_end}"
        """.strip()

    quiet = "--quiet --no-warnings" if quiet else ""
    # noqa: E501
    command = f"""
        yt-dlp {quiet} -x --audio-format wav -f bestaudio -o "{des_path}" {section_arg} "{url_base}{src_path}"  
    """.strip()

    attempts = 0
    while True:
        try:
            subret = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT
            )
        except Exception as ex:
            print(f"[fetch_by_yt_dlp] failure: {ex}")
            attempts += 1
            if attempts >= num_attempts:
                traceback.print_exc()
                return None
        else:
            break

    if output_path.exists():
        return output_path, subret
    else:
        return None, subret
