import nextcord
import asyncio
from nextcord.ext import commands
import yt_dlp

intents = nextcord.Intents.all()
intents.voice_states = True
intents.guilds = True
intents.messages = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
default_youtube_stream_url = "https://www.youtube.com/watch?v=rUxyKA_-grg&ab_channel=LofiGirl"

async def delete_message_after_delay(message, delay=30):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except nextcord.NotFound:
        pass

@bot.event
async def on_ready():
    print('AIM: Привет, Никколо! Готов выполнить любую твою команду.')

# Обработчики команд

@bot.command()
async def join(ctx):
    await ctx.message.delete()
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
        reply = await ctx.send("AIM: Подключился к голосовому каналу.")
    else:
        reply = await ctx.send("AIM: Я уже подключён к голосовому каналу.")
    await delete_message_after_delay(reply)

@bot.command()
async def play_radio(ctx):
    await ctx.message.delete()
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel:
        reply = await ctx.send("AIM: Я не подключён к голосовому каналу. Используйте `!join`, чтобы подключиться.")
        await delete_message_after_delay(reply)
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'song.mp3',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(default_youtube_stream_url, download=False)
            if 'formats' in info:
                audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
                if not audio_url:
                    audio_url = info['formats'][0]['url']
            else:
                audio_url = info['url']
            voice_channel.stop()
            voice_channel.play(nextcord.FFmpegPCMAudio(audio_url), after=lambda e: print('Done', e))
        reply = await ctx.send("AIM: Воспроизведение радио началось.")
    except Exception as e:
        reply = await ctx.send(f"AIM: Возникла ошибка при воспроизведении радио - {str(e)}")

    await delete_message_after_delay(reply)

@bot.command()
async def play_other(ctx, *, url):
    await ctx.message.delete()
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel:
        reply = await ctx.send("AIM: Я не подключён к голосовому каналу. Используйте `!join`, чтобы подключиться.")
        await delete_message_after_delay(reply)
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'song.mp3',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'formats' in info:
                audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
                if not audio_url:
                    audio_url = info['formats'][0]['url']
            else:
                audio_url = info['url']
            voice_channel.stop()
            voice_channel.play(nextcord.FFmpegPCMAudio(audio_url), after=lambda e: print('Done', e))
        reply = await ctx.send("AIM: Воспроизведение видео началось.")
    except Exception as e:
        reply = await ctx.send(f"AIM: Возникла ошибка при воспроизведении - {str(e)}")

    await delete_message_after_delay(reply)

@bot.command()
async def stop(ctx):
    await ctx.message.delete()
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_channel:
        reply = await ctx.send("AIM: Я не подключён к голосовому каналу.")
        await delete_message_after_delay(reply)
        return

    if not voice_channel.is_playing():
        reply = await ctx.send("AIM: В данный момент ничего не воспроизводится.")
        await delete_message_after_delay(reply)
        return

    voice_channel.stop()
    reply = await ctx.send("AIM: Воспроизведение остановлено.")
    await delete_message_after_delay(reply)

@bot.command()
async def thx(ctx):
    await ctx.message.delete()
    reply = await ctx.send("Спасибо за поддержку!!!")
    await delete_message_after_delay(reply)

@bot.command()
async def h(ctx):
    await ctx.message.delete()
    help_message = """
    **AIM: Список доступных команд и инструкция**
    
    **!join** — подключает бота к голосовому каналу, в котором находится пользователь.
    Пример: `!join`

    **!play_radio** — начинает воспроизведение заранее заданного радио.
    Пример: `!play_radio`

    **!play_other <ссылка>** — начинает воспроизведение по предоставленной YouTube ссылке.
    Пример: `!play_other https://www.youtube.com/watch?v=dQw4w9WgXcQ`

    **!stop** — останавливает текущее воспроизведение.
    Пример: `!stop`

    **!thx** — благодарность от бота. Показывает сообщение благодарности в чате.
    Пример: `!thx`

    **!h** — показывает это сообщение с инструкциями.
    Пример: `!h`

    *Для работы команд убедитесь, что бот имеет необходимые разрешения на сервере.*
    """
    message = await ctx.send(help_message)
    await delete_message_after_delay(message)

# Обработчик ошибок
@bot.event
async def on_command_error(ctx, error):
    await ctx.message.delete()
    if isinstance(error, commands.CommandNotFound):
        error_message = "AIM: Эта команда не существует. Пожалуйста, проверьте правильность команды или используйте `!h`, чтобы увидеть список доступных команд."
    else:
        error_message = f"AIM: Произошла ошибка: {str(error)}. Попробуйте ещё раз или проверьте правильность команды с помощью `!h`."

    message = await ctx.send(error_message)
    await delete_message_after_delay(message)

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = f"AIM: Произошла ошибка: {str(args[0])}. Попробуйте ещё раз или обратитесь к администратору."
    for channel in bot.get_all_channels():
        if isinstance(channel, nextcord.TextChannel):
            await channel.send(error_message)

# Логирование событий сервера

@bot.event
async def on_member_join(member):
    log_channel = nextcord.utils.get(member.guild.text_channels, name='bot')  # Замените 'логирование' на имя вашего канала
    if log_channel:
        await log_channel.send(f"AIM: {member.name} присоединился к серверу.")

@bot.event
async def on_member_remove(member):
    log_channel = nextcord.utils.get(member.guild.text_channels, name='bot')  # Замените 'логирование' на имя вашего канала
    if log_channel:
        await log_channel.send(f"AIM: {member.name} покинул сервер.")

@bot.event
async def on_member_update(before, after):
    log_channel = nextcord.utils.get(before.guild.text_channels, name='bot')  # Замените 'логирование' на имя вашего канала
    if log_channel:
        if before.nick != after.nick:
            await log_channel.send(f"AIM: {before.name} изменил ник на {after.nick}.")
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]
            if added_roles:
                await log_channel.send(f"AIM: {after.name} получил роли: {', '.join(role.name for role in added_roles)}.")
            if removed_roles:
                await log_channel.send(f"AIM: {after.name} потерял роли: {', '.join(role.name for role in removed_roles)}.")

@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = nextcord.utils.get(member.guild.text_channels, name='bot')  # Замените 'логирование' на имя вашего канала
    if log_channel:
        if before.channel is None and after.channel is not None:
            await log_channel.send(f"AIM: {member.name} присоединился к голосовому каналу {after.channel.name}.")
        elif before.channel is not None and after.channel is None:
            await log_channel.send(f"AIM: {member.name} покинул голосовой канал {before.channel.name}.")
        elif before.channel != after.channel:
            await log_channel.send(f"AIM: {member.name} переместился из голосового канала {before.channel.name} в голосовой канал {after.channel.name}.")

bot.run('YOUR_BOT_TOKEN')  # Замените YOUR_BOT_TOKEN на токен вашего бота


