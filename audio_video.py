import streamlit as st
import os
import numpy as np

from moviepy.editor import VideoFileClip
from moviepy.editor import AudioFileClip

from pydub import AudioSegment
from pydub.silence import split_on_silence



st.set_page_config(
    page_title="Media Studio",
    layout="wide"
)

st.title(" Media Mixing & Audio Engineering Studio")



VIDEO_PATH = "10sec.mp4"
AUDIO_PATH = "ADSS.mp3"



def replace_audio(video_path, audio_path, output_path):

    video = VideoFileClip(video_path)

    audio = AudioFileClip(audio_path)

    # Trim audio if longer
    if audio.duration > video.duration:

        audio = audio.subclip(0, video.duration)

    final_video = video.set_audio(audio)

    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )


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



def reduce_noise(audio_segment, threshold=500):

    samples = np.array(
        audio_segment.get_array_of_samples()
    )

    filtered = np.where(
        np.abs(samples) < threshold,
        0,
        samples
    )

    cleaned_audio = audio_segment._spawn(
        filtered.astype(np.int16).tobytes()
    )

    return cleaned_audio



if st.button("Replace Video Audio"):

    output_video = "final_output.mp4"

    replace_audio(
        VIDEO_PATH,
        AUDIO_PATH,
        output_video
    )

    st.success(" Audio replaced successfully!")

    st.video(output_video)

    with open(output_video, "rb") as file:

        st.download_button(
            label="⬇ Download Video",
            data=file,
            file_name="final_output.mp4",
            mime="video/mp4"
        )



if st.button("🔇 Clean Audio"):

    sound = AudioSegment.from_file(AUDIO_PATH)

    cleaned = remove_silence(sound)

    cleaned = reduce_noise(cleaned)

    output_audio = "cleaned_audio.wav"

    cleaned.export(output_audio, format="wav")

    st.success("✅ Audio cleaned successfully!")

    st.audio(output_audio)

    with open(output_audio, "rb") as file:

        st.download_button(
            label="⬇ Download Cleaned Audio",
            data=file,
            file_name="cleaned_audio.wav",
            mime="audio/wav"
        )


st.subheader(" Media Files")

if os.path.exists(VIDEO_PATH):

    st.success(f"Video Found: {VIDEO_PATH}")

else:

    st.error("10sec.mp4 not found")


if os.path.exists(AUDIO_PATH):

    st.success(f"Audio Found: {AUDIO_PATH}")

else:

    st.error(" ADSS.mp3 not found")
