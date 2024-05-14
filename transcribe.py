# Installing necessary libraries for Deepgram SDK and speech-to-text transcription
! pip install requests ffmpeg-python
! pip install deepgram-sdk==2.12.0
# Deepgram is chosen for speech-to-text transcription due to its accuracy, speed, and ease of use.
# It offers advanced features like punctuation and speaker diarization, making it suitable for various transcription needs.
# Importing required libraries
from deepgram import Deepgram
import json, os

# Setting up Deepgram API key
dg_key = '*******************************'
dg = Deepgram(dg_key)

# Setting the MIME type for the audio file
MIMETYPE = 'mp3'

# Specifying the input audio file
DIRECTORY = 'input.mp3'

# Configuring model parameters for transcription
# The 'general' model is chosen for its versatility and ability to transcribe a wide range of audio content.
# This is a good choice for general-purpose transcription tasks where the content may vary.
# The Nova tier is chosen for its balance of cost and performance.
# It provides reliable transcription results without the high cost of premium tiers, making it suitable for many applications
params = {
    "punctuate": True,  # Add punctuation to the transcript
    "model": 'general',  # Use the general transcription model
    "tier": 'nova'       # Use the Nova tier for transcription
}

# Function to transcribe the audio file
def main():
    audio_file = DIRECTORY
    if audio_file.endswith(MIMETYPE):
        with open(audio_file, "rb") as f:
            source = {"buffer": f, "mimetype": 'audio/' + MIMETYPE}
            # Transcribe the audio file using Deepgram SDK
            res = dg.transcription.sync_prerecorded(source, params)
            # Write the transcription result to a JSON file
            with open(f"./{os.path.splitext(os.path.basename(audio_file))[0]}.json", "w") as transcript:
                json.dump(res, transcript)
    return

# Perform transcription
main()

# Path to the JSON file containing the transcription result
OUTPUT = '/content/input.json'

# Function to segment the transcription into semantic chunks
def semantic_chunking(transcription_file):
    chunks = []
    with open(transcription_file, "r") as file:
        data = json.load(file)
        # Accessing the 'words' key in the JSON data
        words = data['results']['channels'][0]['alternatives'][0]['words']
        current_chunk_text = ""
        current_chunk_start = 0.0
        current_chunk_end = 0.0
        for word in words:
            start_time = word['start']
            end_time = word['end']
            word_text = word['word']
            # Checking if adding the current word would exceed the 15-second limit
            if end_time - current_chunk_start > 15.0:
                # Finalizing the current chunk and starting a new one
                chunks.append({
                    "chunk_id": len(chunks) + 1,
                    "chunk_length": current_chunk_end - current_chunk_start,
                    "text": current_chunk_text.strip(),
                    "start_time": current_chunk_start,
                    "end_time": current_chunk_end
                })
                current_chunk_text = ""
                current_chunk_start = start_time
            current_chunk_text += word_text + " "
            current_chunk_end = end_time
        chunks.append({
            "chunk_id": len(chunks) + 1,
            "chunk_length": current_chunk_end - current_chunk_start,
            "text": current_chunk_text.strip(),
            "start_time": current_chunk_start,
            "end_time": current_chunk_end
        })
    return chunks

# Get semantic chunks
chunks = semantic_chunking(OUTPUT)

# Print the formatted output
for chunk in chunks:
    print(chunk)
