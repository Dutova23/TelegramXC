from aiogram import Bot, Dispatcher, types
from flask import Flask, request
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")  # безопаснее
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = types.Update.model_validate(request.json)
    asyncio.create_task(dp._process_polling_updates([update]))
    return 'ok', 200

@app.route('/')
def home():
    return "Бот работает!", 200

async def on_startup():
    await bot.set_webhook(f"https://your-app-name.onrender.com/{TOKEN}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    app.run(host='0.0.0.0', port=10000)
