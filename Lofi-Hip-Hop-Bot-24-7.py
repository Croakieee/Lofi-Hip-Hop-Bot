import discord
import asyncio
from discord.ext import commands
from discord.voice_client import VoiceClient
import yt_dlp

intents = discord.Intents.all()
intents.voice_states = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
youtube_stream_url = "https://www.youtube.com/watch?v=7NOSDKb0HlU"
#could be any STREAM video url

@bot.event
async def on_ready():
    print(f'AIM: Привет, Никколо! Готов выполнить любую твою команду.')

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    voice_channel = await channel.connect()

@bot.command()
async def play(ctx):
    try:
        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        ydl_opts = {
            'format': 'bestaudio',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': 'song.mp3',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_stream_url, download=False)
            url2 = info['formats'][0]['url']
            voice_channel.play(discord.FFmpegPCMAudio(url2), after=lambda e: print('Done', e))
        
        await asyncio.sleep(30)

    except Exception as e:
        await ctx.send(f"AIM: Возникла ошибка - {str(e)}")

@bot.command()
async def thx(ctx):
    await ctx.send("AIM: Спасибо за поддержку! Всегда рад помочь!!!")

bot.run('bottoken')
        
