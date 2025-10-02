import retriveveAllSongs, makeHints, download
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
import os
import re
import asyncio
from difflib import SequenceMatcher
import glob

load_dotenv()

# Chooses a random song within your spotify playlist
def getRandSong(songs):
    randChoice = random.randint(0,len(songs))
    return randChoice

# Game logic
async def makeGame(ctx, bot, songs):
    score = 0
    choice = getRandSong(songs)
    url = download.scrape(songs[choice])
    download.download(url)
    makeHints.crop()
    makeHints.makeHint(seconds= 2,index= 1)
    
    # Send first hint automatically
    if os.path.exists("hint1.mp3"):
        await ctx.send("🔊 Hint 1:", file=discord.File("hint1.mp3"))

    hintsUsed = await typeAnswer(ctx, bot, songs[choice])

    # Give points based on how many hints were used
    if hintsUsed == 1:
        score += 20
    elif hintsUsed == 2:
        score += 10
    elif hintsUsed == 3:
        score += 5
    elif hintsUsed == 4:
        score += 2
    # Give zero points if round not answered
    elif hintsUsed == 5:
        score += 0
    return score

# Deletes song files after each round
def deleteFiles():
    os.remove('song.mp3')
    for file in glob.glob("*hint*"):
        if file == "makeHints.py":
            continue
        try:
            os.remove(file)
        except Exception as e:
            pass

# Cleans up title to prevent inconsistencies
def cleanTitle(song: str) -> str:
    title = song.split(" - ")[0]
    title = re.sub(r'[\(\[\{<].*?[\)\]\}>]', '', title)
    title = re.sub(r'[^a-zA-Z0-9 /]', '', title)
    # Remove "feat" and everything after
    title = re.split(r'feat', title, flags=re.IGNORECASE)[0].strip()
    return title

# Check if user input is at least 75% correct
def checkAccuracy(userInput: str, correctTitle: str, threshold: float = 0.75) -> bool:
    ratio = SequenceMatcher(None, userInput.lower(), correctTitle.lower()).ratio()
    return ratio >= threshold

# Check for user input in discord
async def typeAnswer(ctx, bot, song):
    songTitle = cleanTitle(song)
    hint = 1

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("🎵 Guess the song title! Type your Answer below:")

    while True:
        try:
            userMsg = await bot.wait_for('message', check=check, timeout=120)
            userInput = re.sub(r'[^a-zA-Z0-9 /]', '', userMsg.content).strip()

            # ✅ Use fuzzy match instead of exact match
            if checkAccuracy(userInput, songTitle):
                await ctx.send(f"✅ Correct! The Answer was **{songTitle}**")
                deleteFiles()
                break

            elif userInput.lower() == 'nh' and hint == 1:
                makeHints.makeHint(seconds= 5,index= 2)
                if os.path.exists("hint2.mp3"):
                    await ctx.send("🔊 Hint 2:", file=discord.File("hint2.mp3"))
                hint += 1

            elif userInput.lower() == 'nh' and hint == 2:
                makeHints.makeHint(seconds= 10,index= 3)
                if os.path.exists("hint3.mp3"):
                    await ctx.send("🔊 Hint 3:", file=discord.File("hint3.mp3"))
                hint += 1

            elif userInput.lower() == 'nh' and hint == 3:
                makeHints.makeHint(seconds= 15,index= 4)
                if os.path.exists("hint4.mp3"):
                    await ctx.send("🔊 Hint 4:", file=discord.File("hint4.mp3"))
                hint += 1

            elif userInput.lower() == 'skip':
                await ctx.send(f"❌ Skipped! The correct Answer was **{songTitle}**")
                deleteFiles()
                hint = 5
                break

            # Wrong Answer → auto give next hint
            elif userInput.lower() != songTitle.lower() and hint == 1:
                await ctx.send("❌ Wrong Answer, here’s another hint:")
                makeHints.makeHint(seconds= 5,index= 2)
                if os.path.exists("hint2.mp3"):
                    await ctx.send("🔊 Hint 2:", file=discord.File("hint2.mp3"))
                hint += 1

            elif userInput.lower() != songTitle.lower() and hint == 2:
                await ctx.send("❌ Wrong Answer, here’s another hint:")
                makeHints.makeHint(seconds= 10,index= 3)
                if os.path.exists("hint3.mp3"):
                    await ctx.send("🔊 Hint 3:", file=discord.File("hint3.mp3"))
                hint += 1

            elif userInput.lower() != songTitle.lower() and hint == 3:
                await ctx.send("❌ Wrong Answer, last hint coming up:")
                makeHints.makeHint(seconds= 15,index= 4)
                if os.path.exists("hint4.mp3"):
                    await ctx.send("🔊 Hint 4:", file=discord.File("hint4.mp3"))
                hint += 1

            elif userInput.lower() != songTitle.lower() and hint == 4:
                hint += 5
                await ctx.send(f"❌ Out of hints! The correct Answer was **{songTitle}**")
                deleteFiles()
                break

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time’s up! The correct Answer was **{songTitle}**")
            deleteFiles()
            break

    return hint


async def main(ctx, bot, playlist,):
    songs = retriveveAllSongs.fetchSongs(playlist)
    score = 0
    for i in range(5):
        scorePerGame = await makeGame(ctx, bot, songs)
        if i < 4:
            await ctx.send("🔃 Loading song...")

        score += scorePerGame

    await ctx.send(f"🎵 Game over! Your total score is: {score}/100")

if __name__ == '__main__':
    discordToken = str(os.getenv('DISCORD_TOKEN'))
    intents = discord.Intents.default()
    intents.message_content = True  # Important to read message content

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.command()
    async def wpy(ctx, *, playlist: str):
        await ctx.send(f"🤞Starting game...")
        await ctx.send("🔃 Loading first song...")
        await main(ctx, bot, playlist)


    bot.run(discordToken)