from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import RPG_RACES, RPG_GENDERS, FAR_LANDS_START_ID, RPG_CLASSES
from .keyboards import get_main_keyboard
# Видаляємо прямий імпорт show_story_menu тут, щоб уникнути циклу, якщо він є
# import game.story_menu as story_menu (краще імпортувати всередині функції)
import database as db
import ai.core as ai_engine
import json

char_router = Router()

# --- СТАНИ ДЛЯ СТВОРЕННЯ ГЕРОЯ ---
class CharacterCreation(StatesGroup): 
    choosing_race = State()
    choosing_gender = State()
    choosing_age = State()
    choosing_class = State()

# --- МЕНЮ СТАТУСУ ---
@char_router.message(F.text == "👤 Статус")
async def btn_stat(message: types.Message):
    uid = message.from_user.id
    
    res = db.get_full_player_stats(uid)
    if not res:
        await message.answer("Героя ще не створено. Натисніть /start.")
        return
    
    race, gender, age, char_class, level, xp, hp, mhp, mp, mmp, sp, msp, is_fight, rep = res
    loc_info = db.get_user_info(uid)
    loc_name = loc_info[0]
    
    rep_status = "Нейтральний"
    if rep >= 50: rep_status = "Герой (Вас люблять)"
    elif rep >= 20: rep_status = "Шанований"
    elif rep <= -50: rep_status = "Злодій (Вас бояться)"
    elif rep <= -20: rep_status = "Підозрілий"
    
    party = db.get_active_companions_text(uid)

    status_text = (
        f"📋 **Паспорт Героя**\n"
        f"👤 **{race}** ({gender}, {age} років)\n"
        f"⚔️ Клас: {char_class}\n"
        f"🛡 Рівень: {level} (XP: {xp})\n"
        f"--------------------------\n"
        f"❤️ Здоров'я: {hp} / {mhp}\n"
        f"🔮 Мана: {mp} / {mmp}\n"
        f"⚡ Витривалість: {sp} / {msp}\n"
        f"--------------------------\n"
        f"📈 Репутація: {rep} ({rep_status})\n"
        f"📍 Місцезнаходження: {loc_name}\n\n"
        f"👥 **Ваша група:**\n{party}"
    )
    
    await message.answer(status_text)

# --- ОБРОБКА ДАНИХ З WEB APP ---
@char_router.message(lambda m: m.web_app_data and "CREATE_CHARACTER" in m.web_app_data.data)
async def web_app_create_hero(message: types.Message, state: FSMContext):
    try:
        data = json.loads(message.web_app_data.data)
        uid = message.from_user.id
        
        race = data.get("race")
        gender = data.get("gender")
        age = data.get("age")
        char_class = data.get("class")

        db.save_character_data(uid, race, gender, age, char_class)
        db.update_user_location(uid, FAR_LANDS_START_ID)

        await message.answer(
            f"✅ **Героя створено!**\n"
            f"Вітаємо, {race} {char_class}!",
            reply_markup=get_main_keyboard()
        )

        await ai_engine.run_ai_start(message, state)

    except Exception as e:
        print(f"Error creating hero: {e}")
        await message.answer("⚠️ Помилка створення героя.")

# --- СТАРИЙ WIZARD (Залишаємо для сумісності, якщо WebApp не спрацює) ---
@char_router.callback_query(CharacterCreation.choosing_race, F.data.startswith("race_"))
async def process_race(callback: types.CallbackQuery, state: FSMContext):
    race_name = callback.data.split("_")[1]
    await state.update_data(race=race_name)
    builder = InlineKeyboardBuilder()
    for key, value in RPG_GENDERS.items(): builder.button(text=value, callback_data=f"gender_{key}")
    await callback.message.answer(f"Раса: {race_name}. Стать:", reply_markup=builder.adjust(2).as_markup())
    await state.set_state(CharacterCreation.choosing_gender)
    await callback.answer()

@char_router.callback_query(CharacterCreation.choosing_gender, F.data.startswith("gender_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender_key = callback.data.split("_")[1]
    val = RPG_GENDERS.get(gender_key, "-")
    await state.update_data(gender=val)
    await callback.message.edit_text("Вік (число):")
    await state.set_state(CharacterCreation.choosing_age)
    await callback.answer()

@char_router.message(CharacterCreation.choosing_age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return
    await state.update_data(age=int(message.text))
    builder = InlineKeyboardBuilder()
    for cls in RPG_CLASSES.keys(): builder.button(text=cls, callback_data=f"class_{cls}")
    await message.answer("Клас:", reply_markup=builder.adjust(2).as_markup())
    await state.set_state(CharacterCreation.choosing_class)

@char_router.callback_query(CharacterCreation.choosing_class, F.data.startswith("class_"))
async def process_class(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    char_class = callback.data.split("_")[1]
    uid = callback.from_user.id
    db.save_character_data(uid, data['race'], data['gender'], data['age'], char_class)
    await callback.message.edit_text(f"✅ Герой готовий!")
    await state.clear()
    await callback.message.answer("⚔️ **Старт...**", reply_markup=get_main_keyboard())
    await ai_engine.run_ai_start(callback.message, state)
    await callback.answer()