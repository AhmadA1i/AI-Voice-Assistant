# Install required packages

!pip install openai-whisper groq gtts gradio
!pip install twilio
import os
os.environ["GROQ_API_KEY"] = "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"
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import whisper
from groq import Groq
from gtts import gTTS
import requests
import os

app = Flask(__name__)

# Load the Whisper model
model = whisper.load_model("base")

# Initialize Groq client with API key (set your Groq API key in environment variables)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Function to transcribe audio using Whisper
def transcribe_audio(audio_file):
    result = model.transcribe(audio_file)
    return result['text']

# Function to query the LLM using Groq
def query_llm(transcription):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": transcription,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Function to convert text to speech using gTTS
def text_to_speech(response_text, output_file="response.mp3"):
    tts = gTTS(text=response_text, lang='en')
    tts.save(output_file)
    return output_file

# Endpoint to handle incoming Twilio voice requests
@app.route("/voice", methods=["POST"])
def voice():
    # Extract the recording URL from the Twilio request
    recording_url = request.form.get("RecordingUrl")

    # Download the audio from the recording URL
    response = requests.get(f"{recording_url}.wav")
    with open("input_audio.wav", "wb") as f:
        f.write(response.content)

    # Step 1: Transcribe the input audio using Whisper
    transcription = transcribe_audio("input_audio.wav")

    # Step 2: Query the LLM with the transcription
    response_text = query_llm(transcription)

    # Step 3: Convert the LLM response to speech
    audio_file = text_to_speech(response_text)

    # Step 4: Create a Twilio VoiceResponse to play the audio file back to the caller
    twilio_response = VoiceResponse()
    # Replace 'your-server-url' with the actual URL where the Flask app is hosted
    twilio_response.play(url="https://your-server-url.com/response.mp3")

    return Response(str(twilio_response), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
