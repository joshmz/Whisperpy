from pydub import AudioSegment

# Crop mp3 to grab the middle of song
def crop():
    audio = AudioSegment.from_mp3("song.mp3")
    duration = len(audio)/1000
    if duration >= 180:
        startTime = 60 * 1000   # 1 minute
        endTime = 120 * 1000    # 2 minutes
        cropped_audio = audio[startTime:endTime]
        cropped_audio.export("song.mp3", format="mp3")

# Crop mp3 to create hints
def makeHint(seconds, index):
    audio = AudioSegment.from_mp3("song.mp3")
    snippet = audio[:int(seconds * 1000)]
    fileName = f"hint{index}.mp3"
    snippet.export(fileName, format="mp3")