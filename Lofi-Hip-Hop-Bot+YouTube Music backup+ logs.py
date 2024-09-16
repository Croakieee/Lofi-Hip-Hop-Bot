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

async def log_event(message):
    log_channel_name = "bot"  # Название канала для логов
    guild = bot.get_guild(YOUR_GUILD_ID)  # Замените на ID вашего сервера
    if guild:
        log_channel = nextcord.utils.get(guild.text_channels, name=log_channel_name)
        if log_channel:
            await log_channel.send(message)
        else:
            print(f"Не удалось найти канал с названием {log_channel_name}.")
    else:
        print("Не удалось найти сервер.")

@bot.event
async def on_ready():
    print('AIM: Привет, Никколо! Готов выполнить любую твою команду.')
    await log_event("Бот подключён и готов к работе.")

@bot.event
async def on_member_update(before, after):
    # Логирование изменений ника
    if before.display_name != after.display_name:
        message = f"Пользователь {before} изменил ник с {before.display_name} на {after.display_name}."
        await log_event(message)
    
    # Логирование изменений ролей
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    
    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles

    if added_roles:
        roles_names = ", ".join([role.name for role in added_roles])
        message = f"Пользователь {after} получил роли: {roles_names}."
        await log_event(message)

    if removed_roles:
        roles_names = ", ".join([role.name for role in removed_roles])
        message = f"Пользователь {after} потерял роли: {roles_names}."
        await log_event(message)

@bot.event
async def on_member_join(member):
    message = f"Пользователь {member} присоединился к серверу."
    await log_event(message)

@bot.event
async def on_member_remove(member):
    message = f"Пользователь {member} покинул сервер."
    await log_event(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        message = f"Пользователь {member} присоединился к голосовому каналу {after.channel}."
        await log_event(message)
    elif before.channel is not None and after.channel is None:
        message = f"Пользователь {member} покинул голосовой канал {before.channel}."
        await log_event(message)
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        message = f"Пользователь {member} переместился из канала {before.channel} в канал {after.channel}."
        await log_event(message)

    # Логирование включения/выключения микрофона
    if before.mute != after.mute:
        if after.mute:
            message = f"Пользователь {member} включил микрофон."
        else:
            message = f"Пользователь {member} выключил микрофон."
        await log_event(message)

    # Логирование включения/выключения камеры и демонстрации экрана
    if before.self_deaf != after.self_deaf:
        if after.self_deaf:
            message = f"Пользователь {member} включил собственное отключение звука."
        else:
            message = f"Пользователь {member} выключил собственное отключение звука."
        await log_event(message)

    if before.self_mute != after.self_mute:
        if after.self_mute:
            message = f"Пользователь {member} включил собственное отключение микрофона."
        else:
            message = f"Пользователь {member} выключил собственное отключение микрофона."
        await log_event(message)

@bot.command()
async def join(ctx):
    await ctx.message.delete()
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
        reply = await ctx.send("AIM: Подключился к голосовому каналу.")
        await log_event(f"Бот подключился к голосовому каналу {channel}.")
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

    **!del_messages <количество>** — удаляет указанное количество сообщений. 
    Пример: `!del_messages 50`

    **!h** — показывает это сообщение с инструкциями.
    Пример: `!h`

    *Для работы команд убедитесь, что бот имеет необходимые разрешения на сервере.*
    """
    message = await ctx.send(help_message)
    await delete_message_after_delay(message)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def del_messages(ctx, amount: int):
    if amount < 1 or amount > 100:
        reply = await ctx.send("AIM: Введите количество сообщений от 1 до 100.")
        await delete_message_after_delay(reply)
        return

    # Удаляем команду сама по себе, добавив 1 к количеству
    deleted = await ctx.channel.purge(limit=amount + 1)
    reply = await ctx.send(f"AIM: Удалено {len(deleted) - 1} сообщений.")  # -1 потому что команда сама удаляется
    await delete_message_after_delay(reply)

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

# Замените YOUR_BOT_TOKEN на токен вашего бота
bot.run('YOUR_BOT_TOKEN')
