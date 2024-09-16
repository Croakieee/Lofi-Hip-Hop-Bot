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

bot = commands.Bot(intents=intents)
default_youtube_stream_url = "https://www.youtube.com/watch?v=rUxyKA_-grg&ab_channel=LofiGirl"

# Создаем словари для отслеживания времени последнего сообщения пользователя и предупреждений
last_message_time = {}
spam_warning_sent = set()
user_warnings = {}

async def delete_message_after_delay(message, delay=30):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except nextcord.NotFound:
        pass

async def log_event(message):
    log_channel_name = "логи-🌐"  # Название канала для логов
    guild = bot.get_guild(1284971289261379664)  # Замените на ID вашего сервера
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

    if before.self_mute != after.self_mute:
        if after.self_mute:
            message = f"Пользователь {member} выключил микрофон в канале {after.channel}."
        else:
            message = f"Пользователь {member} включил микрофон в канале {after.channel}."
        await log_event(message)

    if before.self_deaf != after.self_deaf:
        if after.self_deaf:
            message = f"Пользователь {member} выключил звук в канале {after.channel}."
        else:
            message = f"Пользователь {member} включил звук в канале {after.channel}."
        await log_event(message)

    if before.mute != after.mute:
        if after.mute:
            message = f"Пользователь {member} был отключён на сервере в канале {after.channel}."
        else:
            message = f"Пользователь {member} был включён на сервере в канале {after.channel}."
        await log_event(message)

    if before.deaf != after.deaf:
        if after.deaf:
            message = f"Пользователь {member} был отключён на сервере (глухой) в канале {after.channel}."
        else:
            message = f"Пользователь {member} был включён на сервере (не глухой) в канале {after.channel}."
        await log_event(message)

@bot.event
async def on_member_ban(guild, user):
    message = f"Пользователь {user} был забанен на сервере {guild}."
    await log_event(message)

@bot.event
async def on_member_unban(guild, user):
    message = f"Пользователь {user} был разбанен на сервере {guild}."
    await log_event(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    message_info = f"Сообщение от {message.author} в канале {message.channel} было удалено: {message.content}"
    await log_event(message_info)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    message_info = f"Сообщение от {before.author} в канале {before.channel} было отредактировано:\nДо: {before.content}\nПосле: {after.content}"
    await log_event(message_info)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    message_info = f"Пользователь {user} добавил реакцию {reaction.emoji} к сообщению в канале {reaction.message.channel}."
    await log_event(message_info)

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return
    message_info = f"Пользователь {user} удалил реакцию {reaction.emoji} с сообщения в канале {reaction.message.channel}."
    await log_event(message_info)

@bot.event
async def on_message(message):
    # Игнорируем сообщения от бота
    if message.author == bot.user:
        return

    current_time = asyncio.get_event_loop().time()
    user_id = message.author.id

    # Проверяем, есть ли у пользователя запись времени последнего сообщения
    if user_id in last_message_time:
        time_since_last_message = current_time - last_message_time[user_id]
        if time_since_last_message < 3:
            # Пользователь отправил сообщение слишком быстро, предупреждаем его
            if user_id not in spam_warning_sent:
                await message.channel.send(f"{message.author.mention}, не спамьте! Пожалуйста, отправляйте сообщения не чаще, чем раз в 3 секунды.")
                spam_warning_sent.add(user_id)
                user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
                
                if user_warnings[user_id] >= 3:
                    member = message.guild.get_member(user_id)
                    if member:
                        role_name = "Muted"
                        muted_role = nextcord.utils.get(message.guild.roles, name=role_name)
                        if not muted_role:
                            try:
                                muted_role = await message.guild.create_role(name=role_name, permissions=nextcord.Permissions(send_messages=False))
                                for channel in message.guild.channels:
                                    await channel.set_permissions(muted_role, send_messages=False)
                            except Exception as e:
                                print(f"Ошибка создания роли: {str(e)}")
                        if muted_role:
                            await member.add_roles(muted_role)
                            await message.channel.send(f"{message.author.mention}, вы были замучены на 5 минут за спам.")
                            await asyncio.sleep(300)  # Мут на 5 минут
                            await member.remove_roles(muted_role)
                            await message.channel.send(f"{message.author.mention}, ваш мут завершён.")
                        user_warnings[user_id] = 0  # Сброс предупреждений после мута
            else:
                # Обновляем время последнего сообщения
                last_message_time[user_id] = current_time
        else:
            # Обновляем время последнего сообщения
            last_message_time[user_id] = current_time
            if user_id in spam_warning_sent:
                spam_warning_sent.remove(user_id)
                user_warnings[user_id] = user_warnings.get(user_id, 0) - 1
    else:
        # Устанавливаем время первого сообщения пользователя
        last_message_time[user_id] = current_time

    # Обрабатываем команды
    await bot.process_commands(message)

@bot.slash_command(name="join", description="Подключить бота к голосовому каналу")
async def join(interaction: nextcord.Interaction):
    channel = interaction.user.voice.channel
    if not interaction.guild.voice_client:
        await channel.connect()
        await interaction.response.send_message("AIM: Подключился к голосовому каналу.", ephemeral=True)
        await log_event(f"Бот подключился к голосовому каналу {channel}.")
    else:
        await interaction.response.send_message("AIM: Я уже подключён к голосовому каналу.", ephemeral=True)

@bot.slash_command(name="play_radio", description="Начать воспроизведение радио")
async def play_radio(interaction: nextcord.Interaction):
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_channel:
        await interaction.response.send_message("AIM: Я не подключён к голосовому каналу. Используйте /join, чтобы подключиться.", ephemeral=True)
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
        await interaction.response.send_message("AIM: Воспроизведение радио началось.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"AIM: Возникла ошибка при воспроизведении радио - {str(e)}", ephemeral=True)

@bot.slash_command(name="play_other", description="Начать воспроизведение по ссылке")
async def play_other(interaction: nextcord.Interaction, url: str):
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_channel:
        await interaction.response.send_message("AIM: Я не подключён к голосовому каналу. Используйте /join, чтобы подключиться.", ephemeral=True)
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
        await interaction.response.send_message("AIM: Воспроизведение видео началось.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"AIM: Возникла ошибка при воспроизведении - {str(e)}", ephemeral=True)

@bot.slash_command(name="stop", description="Остановить текущее воспроизведение")
async def stop(interaction: nextcord.Interaction):
    voice_channel = nextcord.utils.get(bot.voice_clients, guild=interaction.guild)

    if not voice_channel:
        await interaction.response.send_message("AIM: Я не подключён к голосовому каналу.", ephemeral=True)
        return

    if not voice_channel.is_playing():
        await interaction.response.send_message("AIM: В данный момент ничего не воспроизводится.", ephemeral=True)
        return

    voice_channel.stop()
    await interaction.response.send_message("AIM: Воспроизведение остановлено.", ephemeral=True)
    await log_event("Воспроизведение было остановлено.")

@bot.slash_command(name="leave", description="Отключить бота от голосового канала")
async def leave(interaction: nextcord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client is not None:
        await voice_client.disconnect()
        await interaction.response.send_message("AIM: Отключился от голосового канала.", ephemeral=True)
        await log_event(f"Бот отключился от голосового канала {voice_client.channel}.")
    else:
        await interaction.response.send_message("AIM: Я не подключён к голосовому каналу.", ephemeral=True)

@bot.slash_command(name="thx", description="Сказать спасибо боту")
async def thx(interaction: nextcord.Interaction):
    await interaction.response.send_message("AIM: Рад был помочь! :)", ephemeral=True)

@bot.slash_command(name="del_messages", description="Удалить последние сообщения")
async def del_messages(interaction: nextcord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("AIM: Укажите количество сообщений от 1 до 100.", ephemeral=True)
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"AIM: Удалил {amount} сообщений.", ephemeral=True)
    await log_event(f"Удалено {amount} сообщений пользователем {interaction.user}.")

@bot.slash_command(name="h", description="Показать доступные команды")
async def h(interaction: nextcord.Interaction):
    help_message = """
    **Доступные команды:**

    **/join** — подключить бота к голосовому каналу.
    Пример: /join

    **/leave** — отключить бота от голосового канала.
    Пример: /leave

    **/play_radio** — начать воспроизведение радио.
    Пример: /play_radio

    **/play_other <ссылка>** — начать воспроизведение YouTube видео по ссылке.
    Пример: /play_other https://www.youtube.com/...

    **/stop** — остановить текущее воспроизведение.
    Пример: /stop

    **/thx** — сказать спасибо боту.
    Пример: /thx

    **/del_messages <количество>** — удаляет заданное количество сообщений (от 1 до 100).
    Пример: /del_messages 10
    """
    await interaction.response.send_message(help_message, ephemeral=True)

bot.run('YOUR_BOT_TOKEN_HERE')  # Убедитесь, что заменили 'YOUR_BOT_TOKEN_HERE' на ваш токен бота
