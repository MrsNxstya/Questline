from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID, GLOBAL_MAP_ID
import database as db
from .core import generate_ai_response, StoryMode, USER_OPTIONS

ai_router = Router()

@ai_router.message(Command("stats"))
async def show_event_stats(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    summary = db.get_statistics_summary(uid)
    await message.answer(summary)

# --- ПАУЗА ---
@ai_router.message(Command("pause"))
async def pause_game(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await state.set_state(StoryMode.paused)
    await message.answer("⏸️ **PAUSED**\nAI зупинено. Ви можете використовувати адмін-команди.")

@ai_router.message(Command("resume"))
async def resume_game(message: types.Message, state: FSMContext):
    await message.answer("▶️ **RESUMED**\nГра продовжується.")
    await state.set_state(StoryMode.active)
    # Нагадуємо AI про контекст і продовжуємо з останнього місця
    await generate_ai_response(message, state, "SYSTEM: Resume the story from the exact point where it was paused. Continue the narrative seamlessly without restarting. Remind the player of the current situation briefly if needed, then proceed with the next part of the story.", message.from_user.id)

# --- ОБРОБКА ТЕКСТУ ГРАВЦЯ ---
@ai_router.message(StoryMode.active)
async def ai_story_text_handler(message: types.Message, state: FSMContext):
    # Ігноруємо команди меню, щоб вони не йшли в історію як дії
    if message.text in ["🎒 Інвентар", "👤 Статус", "📜 Квести", "/start", "/restart", "🗺 Карта"]:
        return

    # Команда для виходу з режиму історії
    if message.text.lower() in ["стоп", "вихід"]:
        await state.clear()
        await message.answer("Pause. (Напишіть /resume щоб продовжити або /start для меню)")
        return

    # Показуємо, що бот "друкує"
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Отримуємо історію
    history = db.get_ai_history(message.from_user.id)
    
    # Формуємо запит до AI
    prompt = f"{history}\nUser Action: {message.text}"
    
    # Викликаємо головний мозок
    await generate_ai_response(message, state, prompt, message.from_user.id)

# --- ОБРОБКА КНОПОК ВАРІАНТІВ ---
@ai_router.callback_query(F.data.startswith("aichoice_"))
async def ai_button_handler(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Отримуємо індекс кнопки
        index = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        # Дістаємо текст варіанту з пам'яті
        options = USER_OPTIONS.get(user_id, [])
        
        if index < len(options):
            action_text = options[index]
            
            # Прибираємо кнопки, щоб не можна було натиснути двічі
            await callback.message.edit_reply_markup(reply_markup=None)
            
            # Пишемо в чат, що обрав гравець
            await callback.message.answer(f"👤 **{action_text}**")
            
            # Отримуємо історію
            history = db.get_ai_history(user_id)
            
            # Формуємо запит так, ніби це вже сталося
            prompt = f"{history}\nUser Action: {action_text}"
            
            # Викликаємо AI
            await generate_ai_response(callback.message, state, prompt, user_id)
        else:
            await callback.answer("Ця кнопка застаріла.")
            
    except Exception as e:
        print(f"Button Error: {e}")
        await callback.answer("Помилка обробки кнопки.")

# --- ОБРОБКА КНОПКИ КАРТИ В ІСТОРІЇ ---
@ai_router.callback_query(F.data == "open_map")
async def open_map_in_story(callback: types.CallbackQuery):
    uid = callback.from_user.id

    # Отримуємо ID поточної локації гравця
    loc_id = db.get_user_info(uid)[0]

    # Отримуємо детальну інформацію про локацію та сусідів
    name, desc, _, neighbors = db.get_location_full(loc_id)

    map_text = f"📍 **Ви знаходитесь: {name}**\n_{desc}_\n\n"

    builder = InlineKeyboardBuilder()

    if neighbors:
        map_text += "🛣 **Шляхи ведуть до:**\n"
        for label, dest_name, d_id in neighbors:
            map_text += f"▫️ {label} -> {dest_name}\n"
            builder.button(text=f"🚶 {label}", callback_data=f"map_move_{d_id}")
    else:
        map_text += "🚫 Тупик. Шляхів немає."

    builder.adjust(1)

    # Відправляємо карту як нове повідомлення
    await callback.message.answer_photo(GLOBAL_MAP_ID, caption=map_text, reply_markup=builder.as_markup()) if GLOBAL_MAP_ID else await callback.message.answer(map_text, reply_markup=builder.as_markup())

    await callback.answer()
