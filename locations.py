from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
import database as db

loc_router = Router()

class LocEditor(StatesGroup): 
    waiting_for_id = State()
    waiting_for_text = State()
    waiting_for_media = State()

# === ⛔ СТВОРЕННЯ ЛОКАЦІЙ ВИМКНЕНО (Закоментовано) ===
# (Розкоментуй, якщо терміново треба буде додати технічну точку)

# class QuestBuilder(StatesGroup): 
#     waiting_for_name = State()
#     waiting_for_loc_text = State()
#     waiting_for_loc_media = State()
#     waiting_for_link_data = State()

# @loc_router.message(Command("new_loc"))
# async def nl(message: types.Message):
#     if message.from_user.id != ADMIN_ID: return
#     await message.answer("🚫 Створення локацій вимкнено у Config. Гра керується сюжетом.")

# @loc_router.message(Command("connect"))
# async def nc(message: types.Message):
#      if message.from_user.id != ADMIN_ID: return
#      await message.answer("🚫 Ручні переходи вимкнено.")

# =======================================================


# --- РЕДАГУВАННЯ (ЗАЛИШИЛИ ДЛЯ ВИПРАВЛЕНЬ) ---

@loc_router.message(Command("edit_loc"))
async def el(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    try:
        lid = int(message.text.split()[1])
        await state.update_data(lid=lid)
        await message.answer(f"📝 Редагуємо локацію {lid}.\nВведіть НОВИЙ текст (або `.`):")
        await state.set_state(LocEditor.waiting_for_text)
    except: await message.answer("Format: /edit_loc ID")

@loc_router.message(LocEditor.waiting_for_text)
async def elt(message: types.Message, state: FSMContext):
    await state.update_data(txt=message.text)
    await message.answer("Нове фото (або `.`):")
    await state.set_state(LocEditor.waiting_for_media)

@loc_router.message(LocEditor.waiting_for_media)
async def els(message: types.Message, state: FSMContext):
    d = await state.get_data()
    if message.photo: img = message.photo[-1].file_id
    elif message.text == ".": img = "."
    else: img = None
    
    db.update_location(d['lid'], d['txt'], img)
    await message.answer("✅ Локацію оновлено!")
    await state.clear()