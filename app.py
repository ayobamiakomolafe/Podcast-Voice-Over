import streamlit as st
import os
import time
import shutil
import assemblyai as aai
from elevenlabs import save
import os
import re
import shutil
from moviepy import *
from elevenlabs.client import ElevenLabs


aai.settings.api_key = st.secrets["assemblyai_api_key"]
client = ElevenLabs(api_key= st.secrets["elevenlabs_api_key"])
os.makedirs("temp", exist_ok=True)

text_intro = """A: Hello and welcome to our podcast! I'm your host, Alice.
B: And I'm your co-host, Bob. Today, we're diving into an exciting topic that we know you'll love.
A: That's right! We'll be discussing the latest trends in technology and how they impact our daily lives.
B: Plus, we'll be sharing some personal stories and insights that you won't want to miss."""


def concatenate_audio_moviepy(audio_clip_paths, output_path):
    """Concatenates several audio files into one audio file using MoviePy
    and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
    clips = [AudioFileClip(c) for c in audio_clip_paths]
    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile(output_path)

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def process_audio(input, output, intro_text):
  audio_file = (input)
  config = aai.TranscriptionConfig(speaker_labels=True,)
  transcript = aai.Transcriber().transcribe(audio_file, config)

  
  intro = intro_text.split("\n")
  last_ele  = len(intro)
  
  for ele,i in enumerate(intro):
     if i.split(":")[0].strip() == "A":
       voice = client.generate(
       text=i.split(":")[1].strip(),
       voice="John Englert")
       name = f"intro{ele}.wav"
       path = os.path.join("temp", name)
       save(voice, path)

     elif i.split(":")[0].strip() == "B":
       voice = client.generate(
       text=i.split(":")[1].strip(),
       voice="Susan Englert")
       name = f"intro{ele}.wav"
       path = os.path.join("temp", name)
       save(voice,path)

  name = f"intro{last_ele}.wav"
  path = os.path.join("temp", name)
  shutil.copyfile("intro.wav", path)





  for i,utterance in enumerate(transcript.utterances):
    if utterance.speaker == "A":
      voice = client.generate(
      text=utterance.text,
      voice="John Englert")
      name = f"test{i}.wav"
      path = os.path.join("temp", name)
      save(voice, path)
    elif utterance.speaker == "B":
      voice = client.generate(
      text=utterance.text,
      voice="Susan Englert")
      name = f"test{i}.wav"
      path = os.path.join("temp", name)
      save(voice,path)

  files = os.listdir("temp")
  sorted_files = natural_sort(files)
  paths = []

  for i in sorted_files:
    paths.append("temp/"+i)
  
  
  
  concatenate_audio_moviepy(paths, output)
  shutil.rmtree("temp")
# CSS for aesthetics

st.markdown(
    """
    <style>
        .main {
            background-color: #f9f9f9;
        }
        h1 {
            color: #4CAF50;
            font-family: 'Arial', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #f4f4f4;
        }
        .css-18e3th9 {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    
    # App title and logo
    cols1, cols2 = st.columns([0.1, 0.9], gap="small")
    with cols1:
        st.image("logo.jpeg", use_container_width=True)  # Replace with your logo file
    with cols2: 
        st.title("Podcast Audio Transformer")

        # File upload
        intro_text =  st.text_area("Enter the intro text for the podcast", text_intro, height=200)
        uploaded_file = st.file_uploader("Upload your podcast audio file (MP3/WAV)", type=["mp3", "wav"])

        if uploaded_file and intro_text != "":
            if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
                st.session_state["processed"] = False
                st.session_state["last_uploaded_file"] = uploaded_file.name

            # Save uploaded file
            input_path = "input_audio." + uploaded_file.name.split('.')[-1]
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            # Output file path
            output_path = "output_audio.mp3" 

            # Process the audio using your function
            
            if not st.session_state.get("processed", False):
                with st.spinner("Processing audio..."):
                    process_audio(input_path, output_path, intro_text)
                st.session_state["processed"] = True

            # Audio preview and download
            st.audio(output_path, format="audio/mp3")
            with open(output_path, "rb") as f:
                st.download_button("Download Modified Audio", f, file_name="formatted_audio.mp3")

    # Footer
    st.markdown("---")


from streamlit.web import cli as stcli
from streamlit import runtime
import sys

if __name__ == '__main__':
    main()
