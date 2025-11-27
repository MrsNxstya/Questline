from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from config import GLOBAL_MAP_ID, MAP_LOCATIONS
import database as db

# Встав сюди своє посилання на карту (GitHub Pages)
WEB_APP_MAP_URL = "https://mrsnxstya.github.io/rpg-map/map"

async def show_map(message: types.Message):
    """
    Показує інтерактивну карту світу з поточною локацією гравця.
    """
    uid = message.from_user.id

    # Отримуємо ID поточної локації гравця з бази
    # (Тут важливо, щоб get_user_info повертав ID або ми його діставали окремим запитом)
    # В нашому новому database/users.py get_user_info повертає кортеж.
    # Давайте дістанемо ID прямим запитом для надійності
    
    import sqlite3
    from config import DB_NAME
    conn = sqlite3.connect(DB_NAME)
    res = conn.execute("SELECT current_location_id FROM users WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    current_loc_id = res[0] if res else 1
    
    # Отримуємо інформацію про локацію з бази
    loc_name, loc_desc, _, neighbors = db.get_location_full(current_loc_id)

    # Створюємо текст для карти
    map_text = f"🗺 **Карта Світу**\n\n📍 **Ви знаходитесь: {loc_name}**\n_{loc_desc}_\n\n"

    builder = InlineKeyboardBuilder()

    if neighbors:
        map_text += "🛣 **Доступні напрямки:**\n"
        for label, dest_name in neighbors:
            map_text += f"▫️ {label} -> {dest_name}\n"
            # Можна додати кнопки переміщення прямо під картою, якщо хочеш
            # builder.button(text=f"🚶 {label}", callback_data=f"loc_{to_id}") 
    else:
        map_text += "🚫 Немає доступних шляхів."

    # Кнопка відкриття Web App Карти
    builder.button(text="🌍 Відкрити Мапу", web_app=WebAppInfo(url=f"{WEB_APP_MAP_URL}?loc={current_loc_id}"))
    
    builder.adjust(1)

    # Відправляємо повідомлення
    await message.answer(map_text, reply_markup=builder.as_markup())