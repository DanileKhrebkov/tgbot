import telebot
import requests
import json


TELEGRAM_BOT_TOKEN = "7777996066:AAHzuRqZovhHztgX2yNscR3SPZWF4GEq-Cs"
OPENROUTER_API_KEY = "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"  
MODEL_NAME = "deepseek/deepseek-r1-0528:free"  

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, подключенный к нейросети через OpenRouter. Просто напиши мне что-нибудь, и я отвечу!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": user_input}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )

        if response.status_code == 200:
            result = response.json()
            bot_reply = result['choices'][0]['message']['content']
            bot.reply_to(message, bot_reply)
        else:
            error_msg = f"Ошибка API: {response.status_code}\n{response.text}"
            bot.reply_to(message, error_msg)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()