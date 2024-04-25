import os


def convert_mp4_to_wav(mp4_file, wav_file):
    cmd = 'ffmpeg -i {} -acodec pcm_s16le -ar 48000 {}'
    if wav_file is None or len(wav_file) == 0:
        wav_file = mp4_file.replace('.mp4', '.wav')

    os.system(cmd.format(mp4_file, wav_file))

    segment_duration = 30 * 60
    output_pattern = f"{wav_file.replace('.wav', '')}_%03d.wav"
    cmd = f'ffmpeg -i "{wav_file}" -f segment -segment_time {segment_duration} -c copy "{output_pattern}"'
    os.system(cmd)



