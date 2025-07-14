#8138545020:AAGlFrjmqLEajeTaoylWAWfhM0NR_R6dB88

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ContentType
)
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types.input_file import FSInputFile

import pytesseract
from PIL import Image
import asyncio
import os
from aiogram.client.default import DefaultBotProperties
import re 

#слова для проверки чека
RECEIPT_KEYWORDS = [
    "итого", "кассир", "фиск", "инн", "рнк", "сумма", "оплата", "покупка", 
    "продавец-кассир", "ре трейдинг", "re трейдинг", "ре трейди", "re trading", "house", "xc", "хс",
    "ре трейдинг", "re трейдинг", "ре трейди", "re trading",
    "ре трэйдинг", "ре трэйди", "house", "xc", "хс", "ооо ре", "магазин house", "РЕ Треидинг", "РЕ Tpaйдинг"
]


def is_valid_receipt(text: str) -> bool:
    text = text.lower()
    

    keyword_matches = [word for word in RECEIPT_KEYWORDS if word in text]

    has_inn = bool(re.search(r"\b\d{10}\b", text))  # ИНН — 10 цифр
    has_date = bool(re.search(r"\d{2}[./-]\d{2}[./-]\d{2,4}", text))  # дата
    has_time = bool(re.search(r"\d{2}:\d{2}", text))  # время

    return (
        len(text.splitlines()) >= 5 and
        (len(keyword_matches) >= 2 or (has_inn and has_date and has_time))
    )


TOKEN = "8138545020:AAGlFrjmqLEajeTaoylWAWfhM0NR_R6dB88"

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=MemoryStorage())

user_paths = {}

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я сделал покупку в Правда Кофе", callback_data="PRAVDA")],
        [InlineKeyboardButton(text="Я сделал покупку в XC", callback_data="XC")]
    ])
    
    caption = "Привет, я чат-бот коллабы XC и Правда Кофе. Я помогу получить бонусы за ваши покупи! Выберите ниже вариант где была сделана покупка."

  
    photo = FSInputFile("XC_banner.png")


    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption=caption,
        reply_markup=keyboard
    )

@dp.callback_query()
async def handle_callback(call):
    user_id = call.from_user.id
    data = call.data

    user_paths[user_id] = data

    if data == "PRAVDA":
        await bot.send_message(chat_id=user_id, text="Пожалуйста, отправьте фото чека.")
    elif data == "XC":
        await bot.send_message(chat_id=user_id, text="Пожалуйста, отправьте фото чека.")
    elif data == "has_card":
        await bot.send_message(
    chat_id=user_id,
    text=(
        "<b>Отлично!</b>\nЧтобы получить бонусы, просто перейдите по ссылке ниже и оставьте номер телефона, "
        "к которому привязана ваша карта лояльности “Правда Кофе”. Мы начислим бонус на ваш счёт в течение нескольких дней 🙌\n\n"
        '<a href="https://forms.yandex.ru/u/6800ca3190fa7b0f16cd68a7/">Получить баллы</a>'
    )
)

    elif data == "no_card":
        await bot.send_message(
            chat_id=user_id,
            text=(
                "<b>Не проблема!</b>\n"
        "Пройди регистрацию в программе лояльности по ссылке🫰:\n\n"
        '<a href="https://pravdacoffee.ru/allnews/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B0-%D0%BB%D0%BE%D1%8F%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8-2/">Оформить карту Правда Кофе</a>'
    )
)


@dp.message(F.content_type == ContentType.PHOTO)
async def handle_receipt_photo(message: Message):
    user_id = message.from_user.id
    brand = user_paths.get(user_id)

    if not brand:
        await message.answer("Сначала выберите, где вы совершили покупку — /start")
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)

   
    import uuid
    filename = f"receipt_{user_id}_{uuid.uuid4().hex}.jpg"
    await bot.download_file(file.file_path, filename)

    image = Image.open(filename)
    text = pytesseract.image_to_string(image, lang="rus")
    os.remove(filename)

    if not is_valid_receipt(text):
        await message.answer("❌ Это изображение не похоже на кассовый чек. Убедитесь, что на фото видна сумма, ИНН или дата.")
        return

    text_lower = text.lower()

    if brand == "PRAVDA":
        if "правда" in text_lower:
            promocode = "XC_2025"
            await message.answer(
                f"🥳Чек от Правда Кофе принят!\n\n🎁 Вот ваш промокод для ХС: <b>{promocode}</b>\n"
                "При совершении покупки просто покажите его на кассе!"
            )
        else:
            await message.answer("❌ Не удалось подтвердить бренд Правда Кофе на чеке.\nУбедитесь, что на фото виден логотип или название бренда.")

    elif brand == "XC":
        if "xc" in text_lower or "ре трэйдинг" in text_lower:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ У меня есть карта лояльности Правда Кофе", callback_data="has_card")],
                [InlineKeyboardButton(text="❌ У меня нет карты лояльности Правда Кофе", callback_data="no_card")]
            ])
            await message.answer(
                "🥳Чек от ХС принят!\n\nЕсть ли у вас карта лояльности Правда Кофе?",
                reply_markup=keyboard
            )

    else:
        await message.answer("❌ Не удалось подтвердить бренд ХС на чеке.\nУбедитесь, что на фото виден логотип или название бренда.")




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

