import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Environment variables se credentials lena
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')

credentials = google.oauth2.credentials.Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

youtube = build('youtube', 'v3', credentials=credentials)

# Video Upload Logic
def upload_video(file_path, title, description):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Shorts', 'Viral'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = request.execute()
    print("Video successfully uploaded! Video ID:", response.get('id'))

if __name__ == '__main__':
    # Yahan apni video file ka naam aur Title/Description rakhein
    if os.path.exists('video.mp4'):
        upload_video('video.mp4', 'My Auto Uploaded Video', 'Uploaded via GitHub Actions!')
    else:
        print("No video.mp4 found to upload.")
