from moviepy.editor import VideoFileClip

def convert_mp4_to_wav(mp4_file, wav_file):
    video_clip = VideoFileClip(mp4_file)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(wav_file, codec='pcm_s16le')

