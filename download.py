from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv
import os
from youtubesearchpython import VideosSearch

load_dotenv()

# Get youtube url
def scrape(song):
    videos_search = VideosSearch(song, limit=1)
    result = videos_search.result()

    video_url = result["result"][0]["link"] # type: ignore

    return video_url

def download(url):
    ydl_opts = {
        'quiet': True,        # Suppresses most output
        'no_warnings': True,  # Suppresses warnings
        'format': 'bestaudio/best',  # get best available audio
        'outtmpl': 'song.%(ext)s',  # save as "<title>.ext"
        'ffmpeg_location': os.getenv('FFMPEG_LOCATION'),
        'postprocessors': [{  # extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',   # convert to mp3
            'preferredquality': '192', # bitrate
        }],
    }

    with YoutubeDL(ydl_opts) as ydl: # type: ignore
        ydl.download([url])


scrape("Kanye Power")

