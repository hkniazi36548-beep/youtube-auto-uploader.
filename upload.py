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
        "Mind-Blowing Space Mysteries",
        "Creepy Deep Ocean Facts",
        "Psychology Tricks & Human Brain",
        "Unknown Dark History",
        "AI & Future Technology Warning"
    ]
    selected_category = random.choice(categories)
    
    prompt = f"""You are a master YouTube Shorts creator. 
    Create a highly suspenseful, viral video script about: '{selected_category}'.
    
    CRITICAL RULES:
    1. The script MUST be written in ACTUAL NATIVE URDU TEXT (اردو). Do NOT use Roman Urdu.
    2. Length MUST be exactly around 115-125 words (for 50-55 seconds audio).
    3. Hook (0-3s): Start with a shocking question.
    4. Retention (3-45s): Build suspense. Don't reveal the main secret until the end.
    5. Outro (45-50s): Tell them to subscribe.
    
    Return ONLY a valid JSON object with:
    "script": "Urdu text",
    "query": "English keyword for Pexels (e.g. 'galaxy', 'ai robot')",
    "title": "Title with #Shorts",
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
        print("API error aaya hai. Emergency Backup se random topic uthaya ja raha hai...")
        
        # 4 ALAG ALAG BACKUP TOPICS TA KE VIDEO REPEAT NA HO
        backups = [
            {
                "script": "کیا آپ کو معلوم ہے کہ خلا میں ایک ایسا سیارہ موجود ہے جو پوری طرح ہیرے یعنی ڈائمنڈ سے بنا ہے؟ سائنسدانوں کے مطابق یہ سیارہ زمین سے دو گنا بڑا ہے اور اس کا زیادہ تر حصہ کاربن پر مشتمل ہے۔ ذرا سوچیں اگر انسان کبھی وہاں پہنچ گیا تو کیا ہوگا؟ لیکن وہاں کا درجہ حرارت اتنا زیادہ ہے کہ کوئی بھی چیز سیکنڈوں میں جل کر راکھ بن جائے۔ ایسی ہی مزید دلچسپ اور حیران کن معلومات کے لیے ابھی ہمارے چینل کو سبسکرائب کریں!",
                "query": "space galaxy universe",
                "title": "Heere Se Bana Sayyara! 💎 #Shorts #SpaceFacts",
                "description": "Khala ke hairan kun raaz! \n\n#Shorts #SpaceMysteries #FactsInUrdu #ViralFacts"
            },
            {
                "script": "کیا آپ جانتے ہیں کہ مصر کے اہرام یعنی پیرامڈز کیسے بنائے گئے تھے؟ آج کی جدید ٹیکنالوجی کے باوجود سائنسدان حیران ہیں کہ ہزاروں سال پہلے انسانوں نے اتنے بھاری پتھر اتنی بلندی تک کیسے پہنچائے۔ کچھ لوگوں کا ماننا ہے کہ یہ کام انسانوں کا نہیں بلکہ کسی اور دنیا کی مخلوق یعنی ایلینز کا تھا۔ سچ جو بھی ہو، یہ آج بھی دنیا کا سب سے بڑا راز ہے۔ مزید ایسی پراسرار ویڈیوز کے لیے چینل کو لازمی سبسکرائب کریں!",
                "query": "egypt pyramids mystery",
                "title": "Pyramids Ka Sabse Bara Raaz! 👽 #Shorts #History",
                "description": "Misr ke pyramids kaise bane? \n\n#Shorts #HistoryFacts #Mysteries #UrduFacts"
            },
            {
                "script": "کیا مصنوعی ذہانت یعنی آرٹیفیشل انٹیلیجنس مستقبل میں انسانوں کو ختم کر دے گی؟ آج کل روبوٹس اتنے سمارٹ ہو چکے ہیں کہ وہ خود سے سوچنے اور سیکھنے کی صلاحیت رکھتے ہیں۔ کئی بڑے سائنسدانوں نے وارننگ دی ہے کہ اگر اے آئی کنٹرول سے باہر ہو گئی تو یہ انسانیت کے لیے سب سے بڑا خطرہ بن سکتی ہے۔ کیا ہم اپنے ہی ہاتھوں اپنی تباہی کا سامان تیار کر رہے ہیں؟ مزید جاننے کے لیے ابھی چینل کو سبسکرائب کریں!",
                "query": "ai robot future",
                "title": "AI Insano Ko Khatam Kar Dega? 🤖 #Shorts #Technology",
                "description": "AI aur robots ka khaufnak mustaqbil! \n\n#Shorts #AI #TechFacts #UrduHindiFacts"
            },
            {
                "script": "کیا آپ نے کبھی سوچا ہے کہ ہمارے سمندر کی گہرائی میں کیا چھپا ہے؟ زمین کا اکہتر فیصد حصہ پانی پر مشتمل ہے، لیکن انسان آج تک سمندر کا صرف پانچ فیصد حصہ ہی دریافت کر پایا ہے۔ باقی پچانوے فیصد بالکل اندھیرا اور راز ہے۔ ماریانا ٹرینچ، جو دنیا کی سب سے گہری جگہ ہے، وہاں ایسے عجیب و غریب جانور رہتے ہیں جو بغیر روشنی کے زندہ ہیں۔ ایسی ہی پراسرار اور حیران کن ویڈیوز کے لیے ابھی چینل کو سبسکرائب کریں!",
                "query": "dark deep ocean",
                "title": "Samandar Ka Khaufnak Raaz! 😱 #Shorts #Facts",
                "description": "Samandar ki gehrai ke raaz. \n\n#Shorts #ViralFacts #OceanMysteries #UrduFacts"
            }
        ]
        return random.choice(backups)

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
        
    final_video = final_video.set_audio(audio)
    
    final_duration = min(audio.duration, 55.0)
    final_video = final_video.subclip(0, final_duration)
    
    output_path = "final_output.mp4"
    final_video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='ultrafast')
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
    bg_videos = download_pexels_videos()
    if bg_videos:
        final_vid = create_video(bg_videos, audio)
        if final_vid:
            upload_to_youtube(final_vid)
