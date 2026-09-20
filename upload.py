import os
from PIL import Image

# MoviePy ANTIALIAS Error Fix
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

import random
import asyncio
import requests
import edge_tts
import json
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.fx.all import crop
import moviepy.video.fx.all as vfx
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# API Keys
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_dynamic_content():
    print("ChatGPT se VIRAL aur exact 50-55s ki script banwayi ja rahi hai...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    categories = [
        "Mind-Blowing Space Mysteries",
        "Creepy Deep Ocean Facts",
        "Psychology Tricks & Human Brain",
        "Unknown Dark History",
        "AI & Future Technology Warning"
    ]
    selected_category = random.choice(categories)
    
    prompt = f"""You are a master YouTube Shorts creator. 
    Create a highly suspenseful, viral video script in Roman Urdu/Hindi about: '{selected_category}'.
    
    CRITICAL RULES FOR VIRALITY & DURATION:
    1. The script MUST be exactly between 115 to 125 words. This is strictly required so the audio duration is exactly 50 to 55 seconds. Do NOT write a short script!
    2. Hook (0-3s): Start with a shocking, creepy, or mind-blowing question.
    3. Retention (3-45s): Build suspense. Give insane facts. Don't reveal the main secret until the end.
    4. Outro (45-50s): Tell them to subscribe for more.
    
    Return ONLY a valid JSON object with these exact keys:
    "script": "The 115-125 word voiceover text",
    "query": "1 or 2 simple English keywords for Pexels vertical video search (e.g., 'scary dark', 'galaxy', 'deep ocean', 'ai robot')",
    "title": "A highly clickbaity, viral YouTube title with #Shorts",
    "description": "Engaging description with 5 SEO hashtags"
    """
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9 
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print("API error:", e)
        # Backup exact 50-55s viral script
        return {
            "script": "Kya aapne kabhi socha hai ke hamare samandar ki gehrai mein kya chhupa hai? Zameen ka 71 percent hissa pani par mushtamil hai, lekin insan aaj tak samandar ka sirf 5 percent hissa hi explore kar paya hai. Baqi 95 percent bilkul andhera aur raaz hai. Mariana Trench, jo dunya ki sab se gehri jagah hai, wahan aise ajeeb o ghareeb janwar rehte hain jo bina roshni ke zinda hain. Kuch sciencdaan mante hain ke wahan abhi bhi aisi makhlooq maujood ho sakti hai jo saikron saal pehle khatam ho chuki thi. Agar aap wahan chale jayein toh pani ka pressure aapko seconds mein khatam kar dega. Aisi hi rahasyamayi aur hairan kun videos ke liye abhi channel ko subscribe karein!",
            "query": "dark deep ocean",
            "title": "Samandar Ka Sabse Khaufnak Raaz! 😱 #Shorts #Facts",
            "description": "Samandar ki gehrai ke hairan kun raaz jo aap nahi jante.\n\n#Shorts #ViralFacts #OceanMysteries #UrduFacts #HindiFacts"
        }

content_data = get_dynamic_content()
URDU_SCRIPT = content_data["script"]
VIDEO_QUERY = content_data["query"]
VIDEO_TITLE = content_data["title"]
VIDEO_DESCRIPTION = content_data["description"]

async def generate_voiceover_async():
    print("Voiceover tayar ho raha hai...")
    voice = "ur-PK-AsadNeural" 
    communicate = edge_tts.Communicate(URDU_SCRIPT, voice)
    await communicate.save("voiceover.mp3")
    return "voiceover.mp3"

def generate_voiceover():
    return asyncio.run(generate_voiceover_async())

def download_pexels_video():
    print(f"Pexels se '{VIDEO_QUERY}' download ho rahi hai...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={VIDEO_QUERY}&orientation=portrait&per_page=1"
    response = requests.get(url, headers=headers).json()
    if "videos" in response and len(response["videos"]) > 0:
        video_url = response["videos"][0]["video_files"][0]["link"]
        vid_data = requests.get(video_url)
        with open("background.mp4", "wb") as f:
            f.write(vid_data.content)
        return "background.mp4"
    return None

def create_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Ensure background loops exactly to the audio duration
    if video.duration < audio.duration:
        video = video.fx(vfx.loop, duration=audio.duration)
        
    w, h = video.size
    target_ratio = 9 / 16
    if w / h > target_ratio:
        video = crop(video, width=int(h * target_ratio), height=h, x_center=w/2)
    else:
        video = crop(video, width=w, height=int(w / target_ratio), y_center=h/2)
        
    video = video.resize(height=1920, width=1080)
    video = video.set_audio(audio)
    
    # Strict limit: Max 55 seconds cap just in case AI writes too much
    final_duration = min(audio.duration, 55.0)
    video = video.subclip(0, final_duration)
    
    output_path = "final_output.mp4"
    video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='ultrafast')
    return output_path

def upload_to_youtube(file_path):
    print("YouTube Shorts upload start...")
    creds = Credentials(None, refresh_token=REFRESH_TOKEN, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, token_uri="https://oauth2.googleapis.com/token")
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {'title': VIDEO_TITLE, 'description': VIDEO_DESCRIPTION, 'tags': ['shorts', 'facts', 'viral', 'urdu', 'hindi'], 'categoryId': '22'},
        'status': {'privacyStatus': 'public'}
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    response = request.execute()
    print(f"Shorts successfully upload ho gayi! ID: {response.get('id')}")

if __name__ == "__main__":
    audio = generate_voiceover()
    bg_video = download_pexels_video()
    if bg_video:
        final_vid = create_video(bg_video, audio)
        upload_to_youtube(final_vid)
