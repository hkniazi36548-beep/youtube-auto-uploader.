import os
import requests
import json
from openai import OpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. API Keys load karein
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def generate_video_script():
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a YouTube Shorts script writer."},
            {"role": "user", "content": "Write an engaging 30-second motivational YouTube Short script with title and description."}
        ]
    )
    return response.choices[0].message.content

def main():
    print("Starting automated YouTube content workflow...")
    script = generate_video_script()
    print("Generated Script:")
    print(script)
    print("Workflow step completed successfully!")

if __name__ == "__main__":
    main()
