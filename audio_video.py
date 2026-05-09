import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Media Studio", layout="wide")

st.title("🎬 Media Mixing & Audio Engineering Studio")

# -----------------------------
# Upload Section
# -----------------------------

video_file = st.file_uploader(
    "Upload Video",
    type=["mp4", "mov", "avi"]
)

audio_file = st.file_uploader(
    "Upload Audio",
    type=["mp3", "wav"]
)

music_file = st.file_uploader(
    "Upload Background Music",
    type=["mp3", "wav"]
)

# -----------------------------
# Helper Functions
# -----------------------------

def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


# -----------------------------
# Replace Audio
# -----------------------------

def replace_audio(video_path, audio_path, output):

    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Sync duration
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    final = video.set_audio(audio)

    final.write_videofile(output, codec="libx264", audio_codec="aac")


# -----------------------------
# Add Background Music
# -----------------------------

def add_background_music(video_path, music_path, output, volume=0.3):

    video = VideoFileClip(video_path)
    music = AudioFileClip(music_path).volumex(volume)

    final_audio = video.audio.volumex(1.0)

    mixed_audio = final_audio.audio_fadein(1)

    mixed_audio = mixed_audio.set_duration(video.duration)

    final_audio = mixed_audio

    final = video.set_audio(final_audio)

    final.write_videofile(output, codec="libx264", audio_codec="aac")


# -----------------------------
# Multi Track Mixer
# -----------------------------

def mix_tracks(file1, file2, output):

    sound1 = AudioSegment.from_file(file1)
    sound2 = AudioSegment.from_file(file2)

    combined = sound1.overlay(sound2)

    combined.export(output, format="mp3")


# -----------------------------
# Volume Adjust
# -----------------------------

def adjust_volume(audio_seg, db_change):

    return audio_seg + db_change


# -----------------------------
# Timing Offset
# -----------------------------

def overlay_with_offset(base, overlay, delay_ms=2000):

    return base.overlay(overlay, position=delay_ms)


# -----------------------------
# Silence Removal
# -----------------------------

def remove_silence(audio):

    chunks = split_on_silence(
        audio,
        min_silence_len=500,
        silence_thresh=-40
    )

    combined = AudioSegment.empty()

    for chunk in chunks:
        combined += chunk

    return combined


# -----------------------------
# Noise Reduction
# -----------------------------

def reduce_noise(audio_seg, threshold=500):

    samples = np.array(audio_seg.get_array_of_samples())

    filtered = np.where(np.abs(samples) < threshold, 0, samples)

    new_audio = audio_seg._spawn(filtered.astype(np.int16).tobytes())

    return new_audio


# -----------------------------
# UI Buttons
# -----------------------------

if video_file and audio_file:

    video_path = save_uploaded_file(video_file)
    audio_path = save_uploaded_file(audio_file)

    if st.button("🎵 Replace Video Audio"):

        output = "output_replace.mp4"

        replace_audio(video_path, audio_path, output)

        st.success("Audio Replaced Successfully!")

        st.video(output)

        with open(output, "rb") as f:
            st.download_button(
                "Download Video",
                f,
                file_name="replaced_audio_video.mp4"
            )


if audio_file and music_file:

    audio_path = save_uploaded_file(audio_file)
    music_path = save_uploaded_file(music_file)

    if st.button("🎧 Mix Audio Tracks"):

        output = "mixed_audio.mp3"

        mix_tracks(audio_path, music_path, output)

        st.success("Audio Mixed Successfully!")

        st.audio(output)

        with open(output, "rb") as f:
            st.download_button(
                "Download Mixed Audio",
                f,
                file_name="mixed_audio.mp3"
            )


if audio_file:

    audio_path = save_uploaded_file(audio_file)

    if st.button("🔇 Remove Silence + Reduce Noise"):

        sound = AudioSegment.from_file(audio_path)

        cleaned = remove_silence(sound)

        cleaned = reduce_noise(cleaned)

        output = "cleaned_audio.wav"

        cleaned.export(output, format="wav")

        st.success("Noise Reduction Complete!")

        st.audio(output)

        with open(output, "rb") as f:
            st.download_button(
                "Download Cleaned Audio",
                f,
                file_name="cleaned_audio.wav"
            )
