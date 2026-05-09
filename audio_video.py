
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np
import tempfile
import os

st.title(" Media Mixing & Audio Engineering Studio")

video_file = st.file_uploader(
    "Upload Video File", 
    type=["mp4", "mov", "avi"]
)

audio_file = st.file_uploader(
    "Upload Audio File", 
    type=["mp3", "wav"]
)

music_file = st.file_uploader(
    "Upload Background Music", 
    type=["mp3", "wav"]
)

# ==========================================
# SAVE TEMP FILES
# ==========================================

def save_temp_file(uploaded_file):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(uploaded_file.read())
    return temp.name

# ==========================================
# REPLACE VIDEO AUDIO
# ==========================================

def replace_audio(video_path, audio_path, output):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Sync duration
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    final = video.set_audio(audio)
    final.write_videofile(output, codec="libx264")

# ==========================================
# ADD BACKGROUND MUSIC
# ==========================================

def add_background_music(video_path, music_path, output, volume=0.3):
    video = VideoFileClip(video_path)

    music = AudioFileClip(music_path).volumex(volume)

    if music.duration > video.duration:
        music = music.subclip(0, video.duration)

    final_audio = video.audio.volumex(1.0)

    mixed_audio = final_audio.audio_fadein(1)

    final = video.set_audio(mixed_audio)

    final.write_videofile(output, codec="libx264")

# ==========================================
# MIX MULTIPLE AUDIO TRACKS
# ==========================================

def mix_tracks(file1, file2, output):
    sound1 = AudioSegment.from_file(file1)
    sound2 = AudioSegment.from_file(file2)

    combined = sound1.overlay(sound2)

    combined.export(output, format="mp3")

# ==========================================
# VOLUME CONTROL
# ==========================================

def adjust_volume(audio_path, output, db_change):
    sound = AudioSegment.from_file(audio_path)

    adjusted = sound + db_change

    adjusted.export(output, format="mp3")



def overlay_with_offset(file1, file2, output, delay_ms=2000):
    base = AudioSegment.from_file(file1)
    overlay = AudioSegment.from_file(file2)

    combined = base.overlay(overlay, position=delay_ms)

    combined.export(output, format="mp3")



def remove_silence(audio_path, output):
    sound = AudioSegment.from_file(audio_path)

    chunks = split_on_silence(
        sound,
        min_silence_len=500,
        silence_thresh=-40
    )

    final_audio = sum(chunks)

    final_audio.export(output, format="mp3")



def reduce_noise(audio_path, output, threshold=500):
    sound = AudioSegment.from_file(audio_path)

    samples = np.array(sound.get_array_of_samples())

    filtered = np.where(np.abs(samples) < threshold, 0, samples)

    cleaned_audio = sound._spawn(filtered.astype(np.int16).tobytes())

    cleaned_audio.export(output, format="mp3")



if video_file and audio_file:

    video_path = save_temp_file(video_file)
    audio_path = save_temp_file(audio_file)

    if st.button(" Replace Video"):
      output = "noise_reduced.mp3"

        reduce_noise(audio_path, output, threshold)

        st.success("Noise Reduced!")

        st.audio(output)

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")
st.markdown("✨ Mini Video + Audio Studio inside Browser")
