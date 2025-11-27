# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
# from aiogram.client.session.aiohttp import AiohttpSession # Розкоментуй це для PythonAnywhere

# Імпортуємо налаштування
from config import API_TOKEN

# Імпортуємо модуль бази даних (тепер це папка database)
import database as db

# Імпортуємо роутери (логіку) з наших нових папок
from admin import admin_router  # Адмінка (створення предметів, локацій)
from game import game_router    # Геймплей (інвентар, статус, переміщення)
from ai import ai_router        # Штучний інтелект (сюжет, бої)

# Налаштування логування (щоб бачити помилки в консолі)
logging.basicConfig(level=logging.INFO)

# --- НАЛАШТУВАННЯ ЗАПУСКУ ---

# ВАРІАНТ 1: Для запуску на комп'ютері (без проксі)
bot = Bot(token=API_TOKEN)

# ВАРІАНТ 2: Для запуску на PythonAnywhere (розкоментуй ці 3 рядки нижче, а верхній закоментуй)
# session = AiohttpSession(proxy="http://proxy.server:3128")
# bot = Bot(token=API_TOKEN, session=session)

# Створюємо диспетчер (він керує повідомленнями)
dp = Dispatcher()

# --- ПІДКЛЮЧЕННЯ РОУТЕРІВ ---
# Порядок важливий! Спочатку специфічні (адмін), потім загальні.

dp.include_router(admin_router) # 1. Адмінка
dp.include_router(ai_router)    # 2. AI та Сюжет (перехоплює текст в режимі історії)
dp.include_router(game_router)  # 3. Геймплей (меню, старт)

# --- ГОЛОВНА ФУНКЦІЯ ---
async def main():
    # 1. Ініціалізація бази даних
    # Створить файл game_engine.db і всі таблиці, якщо їх немає
    db.init_db()
    
    print("✅ RPG Bot Started Successfully! (Модульна архітектура)")
    
    # 2. Видаляємо старі оновлення (щоб бот не відповідав на старі повідомлення при запуску)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 3. Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")