import os
import subprocess


def convert_mp4_to_wav(mp4_file, wav_file):
    cmd = 'ffmpeg -i {} -acodec pcm_s16le -ar 48000 {}'
    if wav_file is None or len(wav_file) == 0:
        wav_file = mp4_file.replace('.mp4', '.wav')

    os.system(cmd.format(mp4_file, wav_file))

    segment_duration = 30 * 60
    output_pattern = f"{wav_file.replace('.wav', '')}_%03d.wav"
    cmd = f'ffmpeg -i "{wav_file}" -f segment -segment_time {segment_duration} -c copy "{output_pattern}"'
    os.system(cmd)


def duration_get(file_path):
    ffprobe_command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    result = subprocess.check_output(ffprobe_command, shell=True, universal_newlines=True)
    duration = float(result)
    return duration


def duration_split(input_dir, output_dir, num_parts=2, file_ext=".wav"):
    if not input_dir:
        print("Input directory not provided.")
        return

    if not output_dir:
        output_dir = os.path.join(input_dir, "output")

    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if file_name.endswith(file_ext):
            file_path = os.path.join(input_dir, file_name)
            duration = duration_get(file_path)
            part_duration = duration / num_parts

            print("[ * ] Duration:", duration)
            print("[ * ] Number of Parts:", num_parts)
            print("[ * ] Part Duration:", part_duration)

            base_name = os.path.splitext(file_name)[0]

            for i in range(num_parts):
                part_output_file = os.path.join(output_dir, f"{base_name}_part{i + 1}{file_ext}")
                start_time = i * part_duration
                ffmpeg_split_command = f'ffmpeg -i "{file_path}" -ss {start_time} -t {part_duration} -c copy "{part_output_file}"'
                subprocess.call(ffmpeg_split_command, shell=True)
