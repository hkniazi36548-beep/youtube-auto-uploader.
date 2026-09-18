import os
from moviepy.editor import ColorClip

def main():
    print("Video creation started...")
    
    # Simple 5 second background test
    clip = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=5)
    
    # Save video
    clip.write_videofile("viral_short.mp4", fps=24)
    print("Video successfully generated!")

if __name__ == "__main__":
    main()
