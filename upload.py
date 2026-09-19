import os
import requests
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. API Keys aur Credentials jo GitHub Secrets se milenge
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# 2. Urdu/Hindi Video ke liye Script (Aap yahan apna topic badal sakte hain)
URDU_SCRIPT = "Kya aap jante hain ke dunya ki sab se khoobsurat aur purisrar jagahon mein se aik Qudrati wadi hai, jahan pani hamesha neela rehta hai? Yeh qudrat ka aik behtareen karishma hai."
VIDEO_QUERY = "nature landscape" # Pexels se video search karne ke liye keyword

def generate_voiceover():
    print("Urdu/Hindi voiceover generate ho raha hai...")
    tts = gTTS(text=URDU_SCRIPT, lang='hi', slow=False) # 'hi' hindi/urdu accent ke liye behtareen kaam karta hai
    tts.save("voiceover.mp3")
    return "voiceover.mp3"

def download_pexels_video():
    print("Pexels se video download ho rahi hai...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={VIDEO_QUERY}&per_page=1"
    response = requests.get(url, headers=headers).json()
    
    if "videos" in response and len(response["videos"]) > 0:
        video_files = response["videos"][0]["video_files"]
        # HD ya sab se behtareen quality wali video link uthana
        video_url = video_files[0]["link"]
        
        vid_data = requests.get(video_url)
        with open("background.mp4", "wb") as f:
            f.write(vid_data.content)
        return "background.mp4"
    else:
        raise Exception("Pexels video nahi mili!")

def create_video():
    audio_path = generate_voiceover()
    video_path = download_pexels_video()
    
    print("Video aur Audio ko jod kar final video ban rahi hai...")
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Video ki lambai audio ke mutabiq set karna (Shorts ke liye max 50-60 sec)
    if video.duration > audio.duration:
        video = video.subclip(0, audio.duration)
    
    final_video = video.set_audio(audio)
    final_video.write_videofile("final_output.mp4", fps=24, codec="libx264", audio_codec="aac")
    return "final_output.mp4"

def upload_to_youtube(file_path):
    print("YouTube par video upload ho rahi hai...")
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    youtube = build("youtube", "v3", credentials=creds)
    
    body = {
        "snippet": {
            "title": "Qudrat ka Karishma | Amazing Facts in Urdu #Shorts",
            "description": "Yeh video khudkar tareeqay se YouTube automation ke zariye banai gayi hai.",
            "tags": ["shorts", "urdufacts", "amazingfacts", "nature"],
            "categoryId": "22" # People & Blogs / Education
        },
        "status": {
            "privacyStatus": "public" # Aap chahein to 'private' bhi rakh sakte hain shuru mein check karne ke liye
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"Video kamyabi ke sath upload ho gayi! Video ID: {response.get('id')}")

if __name__ == "__main__":
    output_file = create_video()
    upload_to_youtube(output_file)
