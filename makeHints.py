from pydub import AudioSegment

# crop mp3
def crop():
    audio = AudioSegment.from_mp3("song.mp3")
    duration = len(audio)/1000
    if duration >= 180:
        start_time = 60 * 1000   # 1 minute
        end_time = 120 * 1000    # 2 minutes
        cropped_audio = audio[start_time:end_time]
        cropped_audio.export("song.mp3", format="mp3")

def makeHint1():
    audio = AudioSegment.from_mp3("song.mp3")
    hint1 = audio[:2000]
    hint1.export("hint1.mp3", format="mp3")

def makeHint2():
    audio = AudioSegment.from_mp3("song.mp3")
    hint2 = audio[:5000]
    hint2.export("hint2.mp3", format="mp3")

def makeHint3():
    audio = AudioSegment.from_mp3("song.mp3")
    hint3 = audio[:10000]
    hint3.export("hint3.mp3", format="mp3")

def makeHint4():
    audio = AudioSegment.from_mp3("song.mp3")
    hint4 = audio[:15000]
    hint4.export("hint4.mp3", format="mp3")
