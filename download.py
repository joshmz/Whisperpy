from yt_dlp import YoutubeDL
import requests
from dotenv import load_dotenv
import os

load_dotenv()

def scrape(song):
    urlList = []
    params: dict = {
        "api_key": os.getenv('SERPAPI_API'),
        "engine": "youtube",
        "search_query": song
    }

    search = requests.get("https://serpapi.com/search", params=params)
    response = search.json()

    for video in response.get("video_results", []):
        urlList.append(video.get('link'))

    url = urlList[0] if urlList else None
    return url

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




