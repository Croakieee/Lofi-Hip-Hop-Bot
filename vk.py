import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# Инициализация с использованием токена группы
vk_session = vk_api.VkApi(token='vk1.a.-dqalGFlMBlc2INvuGcR_x-F29uD5Gtvg9jmmfICsGm4BEfb2I-HHPYt7P9eg-NSDV0TJh3gomMlp55rGK7V9OtmzrDmZlwWyZ2838UyhtnePwY4C4lZH9VYxk7rXSRfw3yQxt-cDpr391-7kJcpowov2J9G-CQZZy4zJxm78U9nGdrTay5tfdtHBDTyv0yAU96dKe5VQD8ignKIiRsQ')
vk = vk_session.get_api()

# Замените 'ID_ГРУППЫ' на ID вашего сообщества
longpoll = VkBotLongPoll(vk_session, -227448794)

# Функция отправки сообщений
def send_message(peer_id, message):
    vk.messages.send(
        peer_id=peer_id,
        message=message,
        random_id=0
    )

# Функция модерации сообщений
def moderate_message(message):
    text = message['text'].lower()
    forbidden_words = ["плохое слово", "другой плохой термин"]
    
    if any(word in text for word in forbidden_words):
        send_message(message['peer_id'], "Пожалуйста, не используйте ненормативную лексику!")
        # Удаление сообщения (требует прав администратора)
        vk.messages.delete(
            message_ids=message['id'],
            delete_for_all=1
        )

# Основной цикл обработки событий
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        message = event.object.message
        peer_id = message['peer_id']
        text = message['text'].lower()
        
        # Проверяем, что это сообщение из беседы
        if peer_id > 2000000000:
            chat_id = peer_id - 2000000000
            print(f"Сообщение из беседы {chat_id}")

            if text == "!help":
                send_message(peer_id, "Команды: !бан, !разбан, !кик, !мут, !размут, !очистить")
            
            elif text.startswith("!бан"):
                try:
                    user_id = int(text.split()[1])
                    vk.groups.ban(group_id=ID_ГРУППЫ, user_id=user_id)
                    send_message(peer_id, f"Пользователь {user_id} забанен.")
                except (IndexError, ValueError):
                    send_message(peer_id, "Использование: !бан [user_id]")
            
            elif text.startswith("!разбан"):
                try:
                    user_id = int(text.split()[1])
                    vk.groups.unban(group_id=ID_ГРУППЫ, user_id=user_id)
                    send_message(peer_id, f"Пользователь {user_id} разбанен.")
                except (IndexError, ValueError):
                    send_message(peer_id, "Использование: !разбан [user_id]")
            
            elif text.startswith("!кик"):
                try:
                    user_id = int(text.split()[1])
                    vk.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
                    send_message(peer_id, f"Пользователь {user_id} кикнут.")
                except (IndexError, ValueError):
                    send_message(peer_id, "Использование: !кик [user_id]")
            
            elif text.startswith("!мут"):
                # Реализуйте логику мута
                send_message(peer_id, "Функция мут реализуется.")
            
            elif text.startswith("!размут"):
                # Реализуйте логику размут
                send_message(peer_id, "Функция размут реализуется.")
            
            elif text.startswith("!очистить"):
                # Реализуйте логику очистки чата
                send_message(peer_id, "Чат очищен (реализуйте логику).")
            
            else:
                moderate_message(message)

