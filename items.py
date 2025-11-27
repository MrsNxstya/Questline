from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import google.generativeai as genai
import json
from config import ADMIN_ID, ITEM_TYPES, RPG_RARITY, GOOGLE_API_KEY
import database as db

items_router = Router()

# --- СТАНИ ---
class ItemBuilder(StatesGroup): 
    name = State()
    type = State()
    rarity = State()
    stats = State()       # Для зброї (Atk/Def)
    effect_info = State() # Для їжі/зілля (Value)
    desc = State()
    image = State()

# --- СТВОРЕННЯ ПРЕДМЕТІВ ---

@items_router.message(Command("new_item"))
async def new_item_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("🛠 **Конструктор предметів**\nВведіть Назву предмету:")
    await state.set_state(ItemBuilder.name)

@items_router.message(ItemBuilder.name)
async def item_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    builder = InlineKeyboardBuilder()
    for item_type in ITEM_TYPES: builder.button(text=item_type, callback_data=f"type_{item_type}")
    await message.answer("Оберіть Тип:", reply_markup=builder.adjust(2).as_markup())
    await state.set_state(ItemBuilder.type)

@items_router.callback_query(ItemBuilder.type, F.data.startswith("type_"))
async def item_type(callback: types.CallbackQuery, state: FSMContext):
    item_type = callback.data.split("_")[1]
    await state.update_data(type=item_type)
    builder = InlineKeyboardBuilder()
    for key, value in RPG_RARITY.items(): builder.button(text=value, callback_data=f"rarity_{key}")
    await callback.message.edit_text(f"Тип: {item_type}. Оберіть Рідкість:", reply_markup=builder.as_markup())
    await state.set_state(ItemBuilder.rarity)

@items_router.callback_query(ItemBuilder.rarity, F.data.startswith("rarity_"))
async def item_rarity(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(rarity=callback.data.split("_")[1])
    data = await state.get_data()
    
    if data['type'] in ["Potion", "Food"]:
        # Гілка для їжі/зілля
        builder = InlineKeyboardBuilder()
        builder.button(text="❤️ HP", callback_data="eff_HP")
        builder.button(text="🔮 MP", callback_data="eff_MP")
        builder.button(text="⚡ SP", callback_data="eff_SP")
        await callback.message.edit_text("Що відновлює цей предмет?", reply_markup=builder.as_markup())
        await state.set_state(ItemBuilder.effect_info)
    else:
        # Гілка для зброї/броні
        await callback.message.edit_text("Введіть Атаку і Захист (напр `10 5`):")
        await state.set_state(ItemBuilder.stats)

# --- ЛОГІКА СТАТІВ ---

@items_router.message(ItemBuilder.stats)
async def item_stats(message: types.Message, state: FSMContext):
    try:
        a, d = map(int, message.text.split())
        await state.update_data(atk=a, defn=d, eff_type=None, eff_val=0) # Немає ефектів
        await message.answer("Введіть Опис предмету:")
        await state.set_state(ItemBuilder.desc)
    except: 
        await message.answer("❌ Помилка. Введіть два числа.")

# Гілка для Їжі/Зілля (Крок 1: Тип ефекту)
@items_router.callback_query(ItemBuilder.effect_info, F.data.startswith("eff_"))
async def item_eff_type(callback: types.CallbackQuery, state: FSMContext):
    effect_type = callback.data.split("_")[1]
    await state.update_data(tmp_eff_type=effect_type)
    await callback.message.edit_text(f"Ефект: {effect_type}. Скільки відновлює? (Введіть число)")
    # Не змінюємо стан, просто чекаємо наступне повідомлення (число)

# Гілка для Їжі/Зілля (Крок 2: Значення ефекту)
@items_router.message(ItemBuilder.effect_info)
async def item_eff_val(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): 
        await message.answer("❌ Тільки число!")
        return
        
    val = int(message.text)
    data = await state.get_data()
    
    # Зберігаємо ефекти, обнуляємо атаку
    await state.update_data(
        atk=0, 
        defn=0, 
        eff_type=data.get("tmp_eff_type"), 
        eff_val=val
    )
    
    await message.answer("Введіть Опис предмету:")
    await state.set_state(ItemBuilder.desc)


# --- ФІНАЛІЗАЦІЯ ---

@items_router.message(ItemBuilder.desc)
async def item_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("🖼 Надішліть фото або напишіть `skip`:")
    await state.set_state(ItemBuilder.image)

@items_router.message(ItemBuilder.image)
async def item_save(message: types.Message, state: FSMContext):
    d = await state.get_data()
    img = message.photo[-1].file_id if message.photo else None
    
    # Додаємо предмет в базу
    nid = db.add_item_template(
        d['name'], d['type'], d['rarity'], 
        d['atk'], d['defn'], 
        d['desc'], img, 
        d['eff_type'], d['eff_val']
    )
    
    info = f"✅ **Предмет створено!** ID: `{nid}`\n"
    if d['eff_type']: info += f"✨ Ефект: +{d['eff_val']} {d['eff_type']}"
    else: info += f"⚔️ {d['atk']} / 🛡 {d['defn']}"
        
    await message.answer(info)
    await state.clear()

# --- AI GENERATOR ---
@items_router.message(Command("gen_loot"))
async def generate_world_loot(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try: count = int(message.text.split()[1])
    except: count = 3
    await message.answer(f"🤖 AI генерує {count} предметів...")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    # Використовуємо нову модель
    model = genai.GenerativeModel('gemini-2.5-flash')

    for i in range(count):
        try:
            prompt = """Create unique RPG item. JSON ONLY: {"name": "Ukr Name", "type": "Weapon/Armor/Potion/Food", "rarity": "Common/Rare", "atk": 0, "def": 0, "effect_type": "HP/MP/SP/null", "effect_val": 0, "desc": "Short desc"}"""
            res = model.generate_content(prompt)
            d = json.loads(res.text.replace("```json", "").replace("```", "").strip())
            
            etype = d.get('effect_type'); etype = None if etype == "null" else etype
            
            db.add_item_template(d['name'], d['type'], d['rarity'], d.get('atk',0), d.get('def',0), d['desc'], None, etype, d.get('effect_val',0))
            await message.answer(f"✅ {d['name']}")
        except: pass
    await message.answer("Done.")

@items_router.message(Command("give"))
async def give(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try: db.give_item_to_user(message.from_user.id, int(message.text.split()[1])); await message.answer("✅ OK")
    except: pass