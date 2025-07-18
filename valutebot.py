from telebot import TeleBot
import json
import requests

bot = TeleBot("7777996066:AAHzuRqZovhHztgX2yNscR3SPZWF4GEq-Cs")

def get_valutes_data():
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

@bot.message_handler(commands=["valute"])
def valute(message):
    try:
        r = get_valutes_data()
        if not r:
            bot.reply_to(message, "Сервис временно недоступен. Попробуйте позже.")
            return
            
        text = message.text.strip().split(' ')[1:]
        if not text:
            bot.reply_to(message, "Введите код валюты (USD) или название (Доллар США)")
            return
            
        query = ' '.join(text).strip()
        
        if query.isupper() and len(query) == 3:
            valute_data = None
            for code, data in r['Valute'].items():
                if code.upper() == query.upper():
                    valute_data = data
                    break
            
            if valute_data:
                response = [
                    f"{valute_data['Name']} ({query}):",
                    f"Курс: {valute_data['Value']} ₽",
                    f"Предыдущий: {valute_data['Previous']} ₽"
                ]
                bot.reply_to(message, '\n'.join(response))
                return
            else:
                bot.reply_to(message, f"Валюта {query} не найдена")
                return
        
        query_lower = query.lower()
        found = []
        
        for code, data in r['Valute'].items():
            if query_lower in data['Name'].lower():
                found.append((code, data))
        
        if not found:
            bot.reply_to(message, f"Валюта '{query}' не найдена")
            return
            
        if len(found) > 1:
            response = [f"Найдено несколько валют:"]
            for code, data in found:
                response.append(f"{code}: {data['Name']} ({data['Value']} ₽)")
            bot.reply_to(message, '\n'.join(response))
            return
            
        code, data = found[0]
        response = [
            f"{data['Name']} ({code}):",
            f"Курс: {data['Value']} ₽",
            f"Предыдущий: {data['Previous']} ₽"
        ]
        bot.reply_to(message, '\n'.join(response))
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
        print(f"Ошибка обработки: {e}")

bot.polling()