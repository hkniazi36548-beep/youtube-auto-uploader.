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
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
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
    print("ChatGPT se naya topic banwaya ja raha hai...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    categories = [
        "Space Mysteries",
        "Deep Ocean Facts",
        "Psychology & Human Brain",
        "Unknown Dark History",
        "AI & Future Technology"
    ]
    selected_category = random.choice(categories)
    
    prompt = f"""You are a master YouTube Shorts creator. 
    Create a highly suspenseful, viral video script about: '{selected_category}'.
    
    CRITICAL RULES:
    1. Script MUST be in PERFECT HINDI (Devanagari script: हिंदी). Do not use English or Roman Hindi.
    2. Length MUST be exactly around 115-125 words (for 50-55 seconds audio).
    3. Return ONLY a valid JSON object with:
    "script": "Hindi text",
    "query": "English keyword for Pexels (e.g. 'galaxy', 'ai robot')",
    "title": "Viral Title in Hindi with #Shorts",
    "description": "Description with hashtags"
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
        print("API error, using backup...")
        backups = [
            {
                "script": "क्या आप जानते हैं कि अंतरिक्ष में एक ऐसा ग्रह है जो पूरी तरह से हीरे यानी डायमंड से बना है? वैज्ञानिकों के अनुसार यह ग्रह पृथ्वी से दोगुना बड़ा है। जरा सोचिए अगर इंसान कभी वहां पहुंच गया तो क्या होगा? लेकिन वहां का तापमान इतना ज्यादा है कि कोई भी चीज सेकंडों में जलकर राख बन जाए। ऐसी ही और रहस्यमयी जानकारियों के लिए अभी सब्सक्राइब करें!",
                "query": "space galaxy universe",
                "title": "हीरे से बना ग्रह! 💎 #Shorts #SpaceFacts",
                "description": "अंतरिक्ष के रहस्य! #Shorts #SpaceMysteries #HindiFacts"
            }
        ]
        return random.choice(backups)

content_data = get_dynamic_content()
HINDI_SCRIPT = content_data["script"]
VIDEO_QUERY = content_data["query"]
VIDEO_TITLE = content_data["title"]
VIDEO_DESCRIPTION = content_data["description"]

async def generate_voiceover_async():
    print("Hindi Specialist Voiceover tayar ho raha hai...")
    voice = "hi-IN-MadhurNeural" 
    communicate = edge_tts.Communicate(HINDI_SCRIPT, voice)
    await communicate.save("voiceover.mp3")
    return "voiceover.mp3"

def generate_voiceover():
    return asyncio.run(generate_voiceover_async())

def download_pexels_videos():
    print(f"Pexels se '{VIDEO_QUERY}' ki Nayi Videos download ho rahi hain...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={VIDEO_QUERY}&orientation=portrait&per_page=20"
    response = requests.get(url, headers=headers).json()
    video_paths = []
    
    if "videos" in response:
        available_videos = response["videos"]
        sample_size = min(4, len(available_videos))
        if sample_size > 0:
            random_videos = random.sample(available_videos, sample_size)
            for i, vid in enumerate(random_videos):
                try:
                    video_url = vid["video_files"][0]["link"]
                    vid_data = requests.get(video_url)
                    file_name = f"bg_video_{i}.mp4"
                    with open(file_name, "wb") as f:
                        f.write(vid_data.content)
                    video_paths.append(file_name)
                except:
                    pass
    return video_paths

def create_video(video_paths, audio_path):
    print("Videos ko merge karke final short banayi ja rahi hai...")
    audio = AudioFileClip(audio_path)
    clips = []
    
    for path in video_paths:
        try:
            clip = VideoFileClip(path)
            w, h = clip.size
            target_ratio = 9 / 16
            if w / h > target_ratio:
                clip = crop(clip, width=int(h * target_ratio), height=h, x_center=w/2)
            else:
                clip = crop(clip, width=w, height=int(w / target_ratio), y_center=h/2)
            clip = clip.resize(height=1920, width=1080)
            clips.append(clip)
        except:
            pass
            
    if not clips:
        return None
        
    final_video = concatenate_videoclips(clips, method="compose")
    
    if final_video.duration < audio.duration:
        final_video = final_video.fx(vfx.loop, duration=audio.duration)
        
    final_duration = min(audio.duration, 55.0)
    final_video = final_video.subclip(0, final_duration)
    final_video = final_video.set_audio(audio)
    
    output_path = "final_output.mp4"
    final_video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='ultrafast')
    return output_path

def upload_to_youtube(file_path):
    print("YouTube Shorts upload start...")
    creds = Credentials(None, refresh_token=REFRESH_TOKEN, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, token_uri="https://oauth2.googleapis.com/token")
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {'title': VIDEO_TITLE, 'description': VIDEO_DESCRIPTION, 'tags': ['shorts', 'facts', 'viral', 'hindi'], 'categoryId': '22'},
        'status': {'privacyStatus': 'public'}
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    response = request.execute()
    print(f"Shorts successfully upload ho gayi! ID: {response.get('id')}")

if __name__ == "__main__":
    audio_file = generate_voiceover()
    bg_videos = download_pexels_videos()
    if bg_videos:
        final_vid = create_video(bg_videos, audio_file)
        if final_vid:
            upload_to_youtube(final_vid)
