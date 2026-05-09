import streamlit as st
import moviepy as mp
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np
import os

st.set_page_config(page_title="Media Studio", layout="wide")

st.title(" Media Mixing & Audio Engineering Studio")

VIDEO_PATH = "10sec.mp4"
AUDIO_PATH = "ADSS.mp3"

def replace_audio(video_path, audio_path, output):

    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Sync audio duration
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    final = video.set_audio(audio)

    final.write_videofile(
        output,
        codec="libx264",
        audio_codec="aac"
    )

def mix_tracks(file1, file2, output):

    sound1 = AudioSegment.from_file(file1)
    sound2 = AudioSegment.from_file(file2)

    combined = sound1.overlay(sound2)

    combined.export(output, format="mp3")

def adjust_volume(audio_seg, db_change):

    return audio_seg + db_change

def overlay_with_offset(base, overlay, delay_ms=2000):

    return base.overlay(overlay, position=delay_ms)

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

def reduce_noise(audio_seg, threshold=500):

    samples = np.array(audio_seg.get_array_of_samples())

    filtered = np.where(
        np.abs(samples) < threshold,
        0,
        samples
    )

    new_audio = audio_seg._spawn(
        filtered.astype(np.int16).tobytes()
    )

    return new_audio

st.subheader(" Replace Video Audio")

if st.button("Replace Audio"):

    output_video = "output_replace.mp4"

    replace_audio(
        VIDEO_PATH,
        AUDIO_PATH,
        output_video
    )

    st.success(" Audio replaced successfully!")

    st.video(output_video)

    with open(output_video, "rb") as f:
        st.download_button(
            "⬇ Download Video",
            f,
            file_name="final_video.mp4"
        )

st.subheader(" Noise Reduction")

if st.button("Clean Audio"):

    sound = AudioSegment.from_file(AUDIO_PATH)

    cleaned = remove_silence(sound)

    cleaned = reduce_noise(cleaned)

    output_audio = "cleaned_audio.wav"

    cleaned.export(output_audio, format="wav")

    st.success("Audio cleaned successfully!")

    st.audio(output_audio)

    with open(output_audio, "rb") as f:
        st.download_button(
            " Download Cleaned Audio",
            f,
            file_name="cleaned_audio.wav"
        )
        
st.subheader(" Current Media Files")

st.write(f"Video File: {VIDEO_PATH}")
st.write(f"Audio File: {AUDIO_PATH}")

if os.path.exists(VIDEO_PATH):
    st.success(" Video file found")

if os.path.exists(AUDIO_PATH):
    st.success(" Audio file found")
