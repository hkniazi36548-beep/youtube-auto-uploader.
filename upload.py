import os
import random
import asyncio
import requests
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. API Keys aur Credentials
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# 2. Mukhtalif Topics aur Scripts ki List
TOPICS_POOL = [
    {
        "script": "Kya aap jante hain ke dunya ki sab se khoobsurat aur purisrar jagahon mein se aik Qudrati wadi hai, jahan pani hamesha neela rehta hai? Yeh qudrat ka aik behtareen karishma hai.",
        "query": "nature landscape",
        "title": "Qudrat Ka Karishma - Amazing Nature #Shorts",
        "description": "Dunya ke khoobsurat aur hairan kun manazir. Yeh qudrat ka aik behtareen karishma hai.\n\n#Shorts #Nature #AmazingFacts #QudratKaKarishma"
    },
    {
        "script": "Kya aapko pata hai ke samandar ki gehrai mein aise aise raaz chhupe hain jo insan ko hairan kar dete hain? Aise hi raazon ko janne ke liye jude rahiye.",
        "query": "deep ocean waves",
        "title": "Samandar Ke Raaz - Ocean Mysteries #Shorts",
        "description": "Samandar ki gehrai aur uske anokhe raaz.\n\n#Shorts #Ocean #Mysteries #Facts"
    },
    {
        "script": "Aasman par chamakte hue sitare aur khali kainaat humein hamesha se apni taraf khinchti hai. Kainaat ki yeh wusat hamari soch se bhi kahin barhi hai.",
        "query": "galaxy stars night sky",
        "title": "Kainaat Ki Wusat - Space Universe #Shorts",
        "description": "Aasman aur kainaat ke anokhe manazir.\n\n#Shorts #Space #Universe #Stars"
    }
]

# Randomly aik topic select hoga har run par
selected_topic = random.choice(TOPICS_POOL)
URDU_SCRIPT = selected_topic["script"]
VIDEO_QUERY = selected_topic["query"]
VIDEO_TITLE = selected_topic["title"]
VIDEO_DESCRIPTION = selected_topic["description"]

async def generate_voiceover_async():
    print("Edge-TTS se professional Urdu/Hindi voiceover generate ho raha hai...")
    # 'ur-PK-AsadNeural' ya 'hi-IN-SwaraNeural' behtareen awaz ke liye
    voice = "hi-IN-SwaraNeural"
    communicate = edge_tts.Communicate(URDU_SCRIPT, voice)
    await communicate.save("voiceover.mp3")
    return "voiceover.mp3"

def generate_voiceover():
    return asyncio.run(generate_voiceover_async())

def download_pexels_video():
    print("Pexels se video download ho rahi hai...")
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
            'tags': ['shorts', 'nature', 'facts', 'urdu', 'hindi'],
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
