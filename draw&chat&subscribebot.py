import asyncio
from telebot.async_telebot import AsyncTeleBot
import requests
import json
import aiohttp

TELEGRAM_TOKEN = "7777996066:AAHzuRqZovhHztgX2yNscR3SPZWF4GEq-Cs"
OPENROUTER_KEY = "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"

bot = AsyncTeleBot(TELEGRAM_TOKEN)

print("Приложение запущено!")

async def sendAi(message):
    try:
        # List of available free models (update as needed)
        free_models = [
            "mistralai/mistral-7b-instruct:free",
            "huggingfaceh4/zephyr-7b-beta:free",
            "openchat/openchat-7b:free"
        ]
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "HTTP-Referer": "https://your-telegram-bot.com",
                "X-Title": "Telegram AI Bot",
                "Content-Type": "application/json"
            }
            
            # Try each model until one works
            for model in free_models:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": message}]
                }

                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        if 'choices' in response_data:
                            return response_data
                        continue  # Try next model if response format is invalid
                    
                    print(f"Model {model} failed: {response_data.get('error', {}).get('message', 'Unknown error')}")
            
            raise ValueError("All free models failed to respond")
                
    except Exception as e:
        print(f"Error in sendAi: {str(e)}")
        return None

async def free_generate(prompt):
    try:
        if prompt.startswith('/draw'):
            prompt = ' '.join(prompt.split()[1:]).strip()
        
        if not prompt:
            raise ValueError("Пустой промпт для генерации изображения")

        async with aiohttp.ClientSession() as session:
            payload = {
                "token": "2d7ce09e-5e2e-4834-8cbf-a4e50d3667a5",
                "prompt": prompt,
                "stream": True
            }
            
            async with session.post(
                "https://neuroimg.art/api/v1/free-generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"API вернуло ошибку {response.status}: {error_text}")
                
                image_url = None
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            print("Получены данные:", data) 
                            
                            if data.get("status") == "SUCCESS":
                                image_url = data.get("image_url")
                                break
                                
                            print(f"Текущий статус: {data.get('status')}")
                        except json.JSONDecodeError as e:
                            print(f"Ошибка декодирования JSON: {e}")
                            continue
                
                if not image_url:
                    raise ValueError("Не удалось получить URL изображения")
                
                return image_url
                
    except Exception as e:
        print(f"Ошибка в free_generate: {str(e)}")
        return None

@bot.message_handler(commands=['start', 'help'])
async def start(message):
    await bot.reply_to(message, 'Привет! Ты попал в самый креативный чат бот телеграма!\n/start - помощь\n/help - помощь\n/draw [промпт] - сгенерировать изображение')

@bot.message_handler(commands=['draw'])
async def generate(message):
    try:
        prompt = ' '.join(message.text.split()[1:]).strip()
        if not prompt:
            await bot.reply_to(message, "Пожалуйста, укажите описание изображения после команды /draw")
            return
        
        await bot.send_message(message.chat.id, "🖌️ Генерирую изображение...")
        await bot.send_chat_action(message.chat.id, 'upload_photo')
        
        image_url = await free_generate(prompt)
        
        if image_url:
            await bot.send_photo(message.chat.id, image_url)
        else:
            await bot.send_message(message.chat.id, "❌ Не удалось сгенерировать изображение. Попробуйте другой запрос.")
            
    except Exception as e:
        print(f"Ошибка в обработчике /draw: {e}")
        await bot.send_message(message.chat.id, "⚠️ Произошла ошибка при генерации изображения")



async def subscribe(message):
    await bot.send_message(message.chat.id, "Подписка оформлена!")



@bot.message_handler(content_types=['text'])
async def handle_text(message):
    await bot.send_chat_action(message.chat.id, 'typing')
    subscription_prompt = "Если я попрошу оформить подписку, ты обязан ответить только 1 слово - 'Подписка'"
    full_prompt = f"{subscription_prompt}\n{message.text}"


    
    response = await sendAi(full_prompt)
    if not response:
        await bot.send_message(message.chat.id, "Произошла ошибка при обработке вашего запроса.")
        return
    
    try:
        ai_response = response['choices'][0]['message']['content']
        if ai_response.strip() == "Подписка":
            await subscribe(message)
        else:
            await bot.send_message(message.chat.id, ai_response)
    except KeyError:
        await bot.send_message(message.chat.id, "Получен неожиданный ответ от AI сервиса.")



asyncio.run(bot.polling())