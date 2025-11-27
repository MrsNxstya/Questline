from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from config import ADMIN_ID, FAR_LANDS_START_ID, RPG_RACES, GLOBAL_MAP_ID
from .keyboards import get_main_keyboard
# Імпортуємо CharacterCreation тільки якщо він потрібен тут
from .character import CharacterCreation 
# Імпортуємо show_story_menu напряму
from .story_menu import show_story_menu
import database as db
import ai.core as ai_engine
import json

nav_router = Router()

# ПОСИЛАННЯ
LAUNCHER_URL = "https://mrsnxstya.github.io/rpg-map/menu"
CHAR_APP_URL = "https://mrsnxstya.github.io/rpg-map/char_creation"
MAP_APP_URL = "https://mrsnxstya.github.io/rpg-map/map"

async def send_level(message: types.Message, lid: int):
    txt, img, trans = db.get_location_data(lid)
    builder = InlineKeyboardBuilder()
    for tid, to_loc, event_id, label in trans:
        if event_id: builder.button(text=f"⚠️ {label}", callback_data=f"event_{event_id}")
        else: builder.button(text=label, callback_data=f"loc_{to_loc}")
    builder.adjust(1)
    
    chat_id = message.chat.id if hasattr(message, 'chat') else message.from_user.id
    if chat_id == ADMIN_ID: txt += f"\n\n🔧 [ID: {lid}]"
    
    try:
        if img and img != ".": await message.bot.send_photo(chat_id, img, caption=txt, reply_markup=builder.as_markup())
        else: await message.bot.send_message(chat_id, txt, reply_markup=builder.as_markup())
    except: await message.bot.send_message(chat_id, txt, reply_markup=builder.as_markup())

# --- СТАРТ ---
@nav_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Перевіряємо чи є герой
    res = db.get_full_player_stats(message.from_user.id)
    start_action = "continue" if res else "new_game"
    
    # Формуємо URL з параметром дії (для меню)
    # Але меню саме може відправити 'new_game' або 'continue'
    # Тому просто відкриваємо меню
    
    kb = InlineKeyboardBuilder()
    # Передаємо URL меню
    kb.button(text="🎮 ВІДКРИТИ ГРУ", web_app=WebAppInfo(url=LAUNCHER_URL))
    
    await message.answer(
        "🌍 **Вітаємо в QuestLine!**\n\nНатисніть кнопку нижче, щоб увійти в світ.",
        reply_markup=kb.as_markup()
    )

# --- ОБРОБКА ДАНИХ З WEB APP (Лаунчер та Створення) ---
@nav_router.message(F.web_app_data)
async def web_app_data_handler(message: types.Message, state: FSMContext):
    raw_data = message.web_app_data.data
    uid = message.from_user.id

    # 1. Обробка команд Лаунчера (прості рядки)
    if raw_data == "continue":
        res = db.get_full_player_stats(uid)
        if not res:
            await message.answer("❌ У вас немає збереженої гри. Почніть нову.")
        else:
            await message.answer("🎮 **Завантаження...**", reply_markup=get_main_keyboard())
            await ai_engine.run_ai_start(message, state)
            
    elif raw_data == "new_game":
        db.clear_ai_history(uid)
        try:
            txt, _, _ = db.get_location_data(1)
            if txt == "Empty": await message.answer("⚠️ Світ порожній!"); return
        except: pass

        db.update_user_location(uid, FAR_LANDS_START_ID)
        
        # Даємо кнопку на Web App створення героя
        kb = InlineKeyboardBuilder()
        kb.button(text="🎭 СТВОРИТИ ГЕРОЯ", web_app=WebAppInfo(url=CHAR_APP_URL))
        
        await message.answer(
            "📜 **Створення персонажа**\nВідкрийте редактор:",
            reply_markup=kb.as_markup()
        )

    # 2. Обробка створення героя (JSON)
    elif "CREATE_CHARACTER" in raw_data:
        try:
            data = json.loads(raw_data)
            db.save_character_data(uid, data['race'], data['gender'], data['age'], data['class'])
            db.update_user_location(uid, FAR_LANDS_START_ID)
            
            await message.answer(f"✅ **Героя створено!**\n{data['race']} {data['class']}", reply_markup=get_main_keyboard())
            await ai_engine.run_ai_start(message, state)
        except Exception as e:
            print(f"Error: {e}")
            await message.answer("Помилка створення.")

# --- РЕСТАРТ ---
@nav_router.message(F.text == "🔄 Рестарт")
@nav_router.message(Command("restart"))
async def btn_restart(message: types.Message, state: FSMContext): 
    await state.clear()
    await cmd_start(message, state)

# --- КАРТА ---
@nav_router.message(F.text == "🗺 Карта")
async def btn_map(message: types.Message):
    uid = message.from_user.id
    import sqlite3
    from config import DB_NAME
    conn = sqlite3.connect(DB_NAME)
    res = conn.execute("SELECT current_location_id FROM users WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    loc_id = res[0] if res else 1
    
    name, desc, _, neighbors = db.get_location_full(loc_id)
    map_text = f"📍 **{name}**\n_{desc}_\n"
    if neighbors: map_text += "\n🛣 **Шляхи:**\n" + "\n".join([f"▫️ {l} -> {d}" for l, d in neighbors])
    else: map_text += "\n🚫 Тупик."

    builder = InlineKeyboardBuilder()
    builder.button(text="🌍 Відкрити Мапу", web_app=WebAppInfo(url=f"{MAP_APP_URL}?loc={loc_id}"))
    await message.answer(map_text, reply_markup=builder.as_markup())

# --- ПЕРЕМІЩЕННЯ ---
@nav_router.callback_query(F.data.startswith("loc_"))
async def on_location_click(c: types.CallbackQuery, state: FSMContext):
    nid = int(c.data.split("_")[1]); uid = c.from_user.id
    if nid == FAR_LANDS_START_ID:
         # Якщо повернулись на старт - пропонуємо нову гру
         kb = InlineKeyboardBuilder()
         kb.button(text="🎭 СТВОРИТИ ГЕРОЯ", web_app=WebAppInfo(url=CHAR_APP_URL))
         await c.message.answer("📜 **Нова гра:**", reply_markup=kb.as_markup())
         await c.message.delete()
         return
    db.update_user_location(uid, nid)
    try: await c.message.delete()
    except: pass
    await send_level(c.message, nid); await c.answer()