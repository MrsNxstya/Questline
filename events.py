from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
import database as db

events_router = Router()

# --- СТАНИ (FSM) ---
class EventBuilder(StatesGroup): 
    name = State()
    chance = State()
    win_lose_ids = State()
    desc = State()
    image = State()

class EventLinker(StatesGroup): 
    data = State()

# --- СТВОРЕННЯ ПОДІЇ (БИТВА/РИЗИК) ---

@events_router.message(Command("new_event"))
async def ne(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("🎲 **Створення Події**\nВведіть Назву події (напр. 'Бій з Орком'):")
    await state.set_state(EventBuilder.name)

@events_router.message(EventBuilder.name)
async def nen(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📊 **Базовий шанс перемоги** (0-100%):\n(Це шанс без урахування бонусів гравця)")
    await state.set_state(EventBuilder.chance)

@events_router.message(EventBuilder.chance)
async def nec(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Тільки число!")
        return
    
    await state.update_data(chance=int(message.text))
    await message.answer("🚪 **Наслідки:**\nВведіть `ID_Перемоги` та `ID_Поразки` через пробіл.\nНаприклад: `5 1` (5 - куди йдемо при успіху, 1 - при невдачі)")
    await state.set_state(EventBuilder.win_lose_ids)

@events_router.message(EventBuilder.win_lose_ids)
async def nel(message: types.Message, state: FSMContext):
    try:
        w, l = map(int, message.text.split())
        await state.update_data(win=w, fail=l)
        await message.answer("📝 **Опис ситуації:**\nНапишіть текст, який побачить гравець перед вибором.")
        await state.set_state(EventBuilder.desc)
    except:
        await message.answer("❌ Помилка. Введіть два числа через пробіл.")

@events_router.message(EventBuilder.desc)
async def ned(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("🖼 **Картинка:**\nНадішліть фото або напишіть `skip`.")
    await state.set_state(EventBuilder.image)

@events_router.message(EventBuilder.image)
async def nei(message: types.Message, state: FSMContext):
    d = await state.get_data()
    img = message.photo[-1].file_id if message.photo else None
    
    eid = db.add_event(d['name'], d['desc'], d['chance'], d['win'], d['fail'], img)
    
    await message.answer(f"✅ **Подію створено!** ID: `{eid}`\nТепер прив'яжіть її до локації через `/link_event`.")
    await state.clear()

# --- ПРИВ'ЯЗКА ПОДІЇ ДО ЛОКАЦІЇ ---

@events_router.message(Command("link_event"))
async def le(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("🔗 **Створення кнопки події**\nВведіть: `ID_Локації ID_Події Текст_Кнопки`\nНаприклад: `2 1 Напасти на ворога`")
    await state.set_state(EventLinker.data)

@events_router.message(EventLinker.data)
async def les(message: types.Message, state: FSMContext):
    try:
        # Розбиваємо тільки перші два пробіли, решта - текст кнопки
        p = message.text.split(maxsplit=2)
        loc_id = int(p[0])
        event_id = int(p[1])
        label = p[2]
        
        db.add_event_transition(loc_id, event_id, label)
        await message.answer("✅ Кнопку події успішно додано!")
    except Exception as e:
        await message.answer(f"❌ Помилка формату або даних: {e}")
    
    await state.clear()