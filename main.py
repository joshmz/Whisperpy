import retriveveAllSongs, makeHints, download
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random
import os
import re
import asyncio
from difflib import SequenceMatcher

load_dotenv()

def getRandSong(songs):
    randChoice = random.randint(0,len(songs))
    return randChoice

async def makeGame(ctx, bot, songs):
    score = 0
    choice = getRandSong(songs)
    url = download.scrape(songs[choice])
    download.download(url)
    makeHints.crop()
    makeHints.makeHint1()
    
    # Send first hint automatically
    if os.path.exists("hint1.mp3"):
        await ctx.send("🔊 Hint 1:", file=discord.File("hint1.mp3"))

    ans = await typeAnswer(ctx, bot, songs[choice])
    if ans == 1:
        score += 20
    elif ans == 2:
        score += 10
    elif ans == 3:
        score += 5
    elif ans == 4:
        score += 2
    elif ans == 5:
        score += 0
    return score



def deleteFiles():
    os.remove('song.mp3')
    os.remove('hint1.mp3')
    if os.path.exists('hint2.mp3'):
        os.remove('hint2.mp3')
    if os.path.exists('hint3.mp3'):
        os.remove('hint3.mp3')
    if os.path.exists('hint4.mp3'):
        os.remove('hint4.mp3')

def cleanTitle(song: str) -> str:
    title = song.split(" - ")[0]
    title = re.sub(r'[\(\[\{<].*?[\)\]\}>]', '', title)
    title = re.sub(r'[^a-zA-Z0-9 /]', '', title)
    # Remove "feat" and everything after
    title = re.split(r'feat', title, flags=re.IGNORECASE)[0].strip()
    return title

def is_close_enough(user_input: str, correct_title: str, threshold: float = 0.75) -> bool:
    """
    Returns True if user_input is similar enough to correct_title.
    threshold = 0.75 means 75% similarity required.
    """
    ratio = SequenceMatcher(None, user_input.lower(), correct_title.lower()).ratio()
    return ratio >= threshold

async def typeAnswer(ctx, bot, song):
    songTitle = cleanTitle(song)
    hint = 1

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("🎵 Guess the song title! Type your answer below:")

    while True:
        try:
            user_msg = await bot.wait_for('message', check=check, timeout=120)
            user_input = re.sub(r'[^a-zA-Z0-9 /]', '', user_msg.content).strip()

            # ✅ Use fuzzy match instead of exact match
            if is_close_enough(user_input, songTitle):
                await ctx.send(f"✅ Correct! The answer was **{songTitle}**")
                deleteFiles()
                break

            elif user_input.lower() == 'nh' and hint == 1:
                makeHints.makeHint2()
                if os.path.exists("hint2.mp3"):
                    await ctx.send("🔊 Hint 2:", file=discord.File("hint2.mp3"))
                hint += 1

            elif user_input.lower() == 'nh' and hint == 2:
                makeHints.makeHint3()
                if os.path.exists("hint3.mp3"):
                    await ctx.send("🔊 Hint 3:", file=discord.File("hint3.mp3"))
                hint += 1

            elif user_input.lower() == 'nh' and hint == 3:
                makeHints.makeHint4()
                if os.path.exists("hint4.mp3"):
                    await ctx.send("🔊 Hint 4:", file=discord.File("hint4.mp3"))
                hint += 1

            elif user_input.lower() == 'skip':
                await ctx.send(f"❌ Skipped! The correct answer was **{songTitle}**")
                deleteFiles()
                hint = 5
                break

            # Wrong answer → auto give next hint
            elif user_input.lower() != songTitle.lower() and hint == 1:
                await ctx.send("❌ Wrong answer, here’s another hint:")
                makeHints.makeHint2()
                if os.path.exists("hint2.mp3"):
                    await ctx.send("🔊 Hint 2:", file=discord.File("hint2.mp3"))
                hint += 1

            elif user_input.lower() != songTitle.lower() and hint == 2:
                await ctx.send("❌ Wrong answer, here’s another hint:")
                makeHints.makeHint3()
                if os.path.exists("hint3.mp3"):
                    await ctx.send("🔊 Hint 3:", file=discord.File("hint3.mp3"))
                hint += 1

            elif user_input.lower() != songTitle.lower() and hint == 3:
                await ctx.send("❌ Wrong answer, last hint coming up:")
                makeHints.makeHint4()
                if os.path.exists("hint4.mp3"):
                    await ctx.send("🔊 Hint 4:", file=discord.File("hint4.mp3"))
                hint += 1

            elif user_input.lower() != songTitle.lower() and hint == 4:
                hint += 5
                await ctx.send(f"❌ Out of hints! The correct answer was **{songTitle}**")
                deleteFiles()
                break

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time’s up! The correct answer was **{songTitle}**")
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