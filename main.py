import os
import time
import requests
from openai import OpenAI
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# 1. API Keys Set Up
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# 2. Viral Motivational Script Generator
def generate_viral_script():
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Write an extremely engaging 15-second YouTube Shorts script about psychology facts or motivation. "
        "Start with a massive curiosity hook in the first 2 seconds. Keep it fast-paced, high energy, crisp, and under 30 words total."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a master YouTube Shorts viral script writer creating content with 10M+ views potential."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 3. High-Quality Audio Generation
def generate_audio(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }
    response = requests.post(url, json=data, headers=headers)
    with open("voice.mp3", "wb") as f:
        f.write(response.content)

# 4. Background Video Download
def get_pexels_video():
    url = "https://api.pexels.com/videos/search?query=dark+motivation&orientation=portrait&per_page=5"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()
    video_url = response['videos'][0]['video_files'][0]['link']
    
    video_data = requests.get(video_url).content
    with open("bg_video.mp4", "wb") as f:
        f.write(video_data)

# 5. Render Final Video
def create_final_video():
    audio = AudioFileClip("voice.mp3")
    video = VideoFileClip("bg_video.mp4").subclip(0, audio.duration)
    
    final_clip = video.set_audio(audio)
    final_clip.write_videofile("viral_short.mp4", fps=30)

def main():
    print("Generating Viral Content...")
    script = generate_viral_script()
    print("Script Created:", script)
    generate_audio(script)
    get_pexels_video()
    create_final_video()

if __name__ == "__main__":
    main()
