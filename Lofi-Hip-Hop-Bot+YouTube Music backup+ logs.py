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

# Логирование событий
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
    if before.display_name != after.display_name:
        message = f"Пользователь {before} изменил ник с {before.display_name} на {after.display_name}."
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

# Остальные команды (play_radio, play_other, stop, thx, h, del_messages) остаются без изменений

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
    await log_event(f"Ошибка: {str(error)}")

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = f"AIM: Произошла ошибка: {str(args[0])}. Попробуйте ещё раз или обратитесь к администратору."
    for channel in bot.get_all_channels():
        if isinstance(channel, nextcord.TextChannel):
            await channel.send(error_message)
    await log_event(f"Ошибка: {str(args[0])}")

# Замените YOUR_BOT_TOKEN на токен вашего бота и YOUR_GUILD_ID на ID вашего сервера
bot.run('YOUR_BOT_TOKEN')
