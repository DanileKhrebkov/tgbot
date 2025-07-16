import telebot
bot = telebot.TeleBot("7777996066:AAHzuRqZovhHztgX2yNscR3SPZWF4GEq-Cs")
user_history = {}
@bot.message_handler(content_types=["text"])
def reply_memory(message):
    user_id = message.from_user.id
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(message.text)
    if len(user_history[user_id]) > 3:
        user_history[user_id] = user_history[user_id][-3:]
    bot.reply_to(message, f"Ваши последние сообщения: \n"+ "\n".join(user_history[user_id]))
bot.polling()