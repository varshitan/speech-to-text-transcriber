# This can take both youtube links and video files as input and transcribe the audio and return the text as an output using gradio
# for video files you can input the path to the video file and it returns the output
#!pip install pytube
import os
import sys
import json
import gradio as gr
from deepgram import Deepgram
from pytube import YouTube

# Setting up Deepgram API key
dg_key = 'daa6f2ccbadf053682f00f4e0dacda1149fe4eaa'
dg = Deepgram(dg_key)

def download_and_transcribe(input_source):
    if 'youtube.com' in input_source:
        yt = YouTube(input_source)
        audio = yt.streams.filter(only_audio=True).first()
        audio_filename = f"{os.path.splitext(yt.title)[0]}.mp3"
        audio.download(output_path='.', filename=audio_filename)
        audio_file = open(audio_filename, "rb")
    else:
        audio_file = open(input_source, "rb")

    # Transcribing the audio
    MIMETYPE = 'mp3'
    source = {"buffer": audio_file, "mimetype": 'audio/' + MIMETYPE}
    res = dg.transcription.sync_prerecorded(source)

    # Semantic Chunking
    chunks = []
    words = res['results']['channels'][0]['alternatives'][0]['words']
    current_chunk_text = ""
    current_chunk_start = 0.0
    current_chunk_end = 0.0
    for word in words:
        start_time = word['start']
        end_time = word['end']
        word_text = word['word']
        if end_time - current_chunk_start > 15.0:
            chunks.append(current_chunk_text.strip())
            current_chunk_text = ""
        current_chunk_text += word_text + " "
        current_chunk_end = end_time
    chunks.append(current_chunk_text.strip())

    return " ".join(chunks)

iface = gr.Interface(
    fn=download_and_transcribe,
    inputs="text",
    outputs="text",
    title="Speech to Text converter",
    description="Upload a YouTube video URL or a local audio file to transcribe the audio and display the text.",
    allow_flagging=False
)

iface.launch()