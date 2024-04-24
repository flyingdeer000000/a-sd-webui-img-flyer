import os


def convert_mp4_to_wav(mp4_file, wav_file):
    cmd = 'ffmpeg -i {} -acodec pcm_s16le -ar 16000 {}'
    if wav_file is None or len(wav_file) == 0:
        wav_file = mp4_file.replace('.mp4', '.wav')
    return os.system(cmd.format(mp4_file, wav_file))

