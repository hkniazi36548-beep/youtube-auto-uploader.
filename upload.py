import os
import random
import asyncio
import requests
import edge_tts
import json
from moviepy.editor import VideoFileClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. API Keys aur Credentials
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_dynamic_content():
    print("ChatGPT se bilkul naya topic aur script banwaya ja raha hai...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    # ChatGPT ko instruction ke har dafa kuch naya banaye
    prompt = """Generate a unique, mind-blowing and interesting fact for a YouTube Short. 
    Return ONLY a valid JSON object (no markdown format, no extra text) with these exactly named keys: 
    "script" (The voiceover text in Roman Urdu/Hindi, around 50-60 words to change duration), 
    "query" (2-3 English words for Pexels video search, e.g., 'mysterious forest', 'space galaxy', 'deep ocean'), 
    "title" (A catchy YouTube title in Roman Urdu or English with #Shorts), 
    "description" (A short description with 4-5 relevant hashtags)."""
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9 # High temperature taake har dafa naya topic aaye
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print("OpenAI API error, default topic use ho raha hai:", e)
        # Agar API fail ho jaye toh yeh backup chalega
        return {
            "script": "Kya aapko pata hai ke dunya ki sabse gehri jagah Mariana Trench hai? Yeh itni gehri hai ke Mount Everest ko bhi isme daal diya jaye toh woh bhi doob jayega.",
            "query": "deep ocean dark",
            "title": "Dunya Ki Sabse Gehri Jagah - Mariana Trench #Shorts",
            "description": "Samandar ke anokhe raaz aur hairan kun facts.\n\n#Shorts #Ocean #Mysteries #Facts"
        }

# ChatGPT se data lena
content_data = get_dynamic_content()
URDU_SCRIPT = content_data["script"]
VIDEO_QUERY = content_data["query"]
VIDEO_TITLE = content_data["title"]
VIDEO_DESCRIPTION = content_data["description"]

async def generate_voiceover_async():
    print("Edge-TTS se professional Urdu/Hindi voiceover generate ho raha hai...")
    voice = "hi-IN-SwaraNeural"
    communicate = edge_tts.Communicate(URDU_SCRIPT, voice)
    await communicate.save("voiceover.mp3")
    return "voiceover.mp3"

def generate_voiceover():
    return asyncio.run(generate_voiceover_async())

def download_pexels_video():
    print(f"Pexels se '{VIDEO_QUERY}' ki video download ho rahi hai...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={VIDEO_QUERY}&per_page=1"
    response = requests.get(url, headers=headers).json()
    if "videos" in response and len(response["videos"]) > 0:
        video_files = response["videos"][0]["video_files"]
        video_url = video_files[0]["link"]
        vid_data = requests.get(video_url)
        with open("background.mp4", "wb") as f:
            f.write(vid_data.content)
        return "background.mp4"
    return None

def create_video(video_path, audio_path):
    print("Video aur audio combine ho rahi hai...")
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    video = video.set_audio(audio)
    video = video.subclip(0, min(video.duration, audio.duration))
    
    output_path = "final_output.mp4"
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    return output_path

def upload_to_youtube(file_path):
    print("YouTube par video upload ho rahi hai...")
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': VIDEO_TITLE,
            'description': VIDEO_DESCRIPTION,
            'tags': ['shorts', 'facts', 'urdu', 'hindi', 'ai'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    response = request.execute()
    print(f"Video successfully upload ho gayi! ID: {response.get('id')}")

if __name__ == "__main__":
    audio = generate_voiceover()
    bg_video = download_pexels_video()
    if bg_video:
        final_vid = create_video(bg_video, audio)
        upload_to_youtube(final_vid)
