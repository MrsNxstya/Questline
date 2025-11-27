from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import RPG_RARITY
import database as db

inv_router = Router()

# --- ЖУРНАЛ ЗАВДАНЬ ---
@inv_router.message(F.text == "📜 Квести")
async def show_quests(message: types.Message):
    user_id = message.from_user.id
    
    # Отримуємо текст активних квестів
    quests_text = db.get_active_quests_text(user_id)
    
    # Отримуємо номер поточної глави
    chapter = db.get_user_chapter(user_id)
    
    await message.answer(
        f"📖 **Глава {chapter}**\n"
        f"------------------------\n"
        f"{quests_text}\n\n"
        f"_(Виконуй завдання, взаємодіючи зі світом через діалог)_"
    )

# --- ПЕРЕГЛЯД ІНВЕНТАРЯ ---
@inv_router.message(F.text == "🎒 Інвентар")
async def show_inventory(message: types.Message):
    user_id = message.from_user.id
    
    # Отримуємо список предметів з бази
    items = db.get_user_inventory(user_id)
    
    if not items:
        await message.answer("Ваш рюкзак порожній.")
        return
    
    builder = InlineKeyboardBuilder()
    
    for item in items:
        # item - це рядок з бази даних (Row)
        icon = RPG_RARITY.get(item['rarity'], "⚪")
        
        # Позначаємо галочкою, якщо предмет одягнений
        mark = "✅" if item['is_equipped'] else ""
        
        button_text = f"{mark} {icon} {item['name']}"
        
        # callback_data містить ID запису в інвентарі (inv_id)
        builder.button(text=button_text, callback_data=f"inv_{item['inv_id']}")
    
    # Виводимо список вертикально (по 1 кнопці в ряд)
    builder.adjust(1)
    
    await message.answer("🎒 **Вміст вашого рюкзака:**", reply_markup=builder.as_markup())

# --- ДЕТАЛІ ПРЕДМЕТУ (Клік по кнопці в інвентарі) ---
@inv_router.callback_query(F.data.startswith("inv_"))
async def inv_click(callback: types.CallbackQuery):
    # Отримуємо ID запису в інвентарі
    inv_id = int(callback.data.split("_")[1])
    
    # Завантажуємо повні дані про предмет
    item = db.get_item_details(inv_id)
    
    if not item:
        await callback.answer("Помилка: предмет не знайдено.")
        return

    status_text = "✅ Одягнено" if item['is_equipped'] else "❌ В рюкзаку"
    
    # Формуємо опис
    info_text = f"**{item['name']}**\n{item['type']} | {RPG_RARITY.get(item['rarity'])}\n"
    
    # Показуємо характеристики залежно від типу
    if item['type'] in ["Potion", "Food"]:
        info_text += f"✨ Ефект: +{item['effect_value']} {item['effect_type']}\n"
    else:
        info_text += f"⚔️ Атака: {item['attack_bonus']} 🛡 Захист: {item['defense_bonus']}\n"
    
    info_text += f"_{item['description']}_\n\nСтатус: {status_text}"
    
    # Створюємо кнопки дій
    builder = InlineKeyboardBuilder()
    
    if item['type'] in ["Potion", "Food"]:
        # Якщо це їжа -> кнопка "Спожити"
        builder.button(text="🍺 Спожити / З'їсти", callback_data=f"consume_{inv_id}")
    else:
        # Якщо це спорядження -> кнопка "Одягнути/Зняти"
        action_label = "Зняти" if item['is_equipped'] else "Одягнути"
        builder.button(text=action_label, callback_data=f"equip_{item['id']}")
    
    builder.button(text="🔙 Закрити", callback_data="close_inv")
    
    # Відправляємо фото або текст
    if item['image_id'] and item['image_id'] != ".":
        await callback.message.answer_photo(item['image_id'], caption=info_text, reply_markup=builder.as_markup())
    else:
        await callback.message.answer(info_text, reply_markup=builder.as_markup())
    
    await callback.answer()

# --- СПОЖИВАННЯ ПРЕДМЕТУ (Їжа/Зілля) ---
@inv_router.callback_query(F.data.startswith("consume_"))
async def consume_handler(callback: types.CallbackQuery):
    inv_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # Викликаємо функцію в базі даних
    result_message = db.consume_item(user_id, inv_id)
    
    # Показуємо результат
    await callback.answer(result_message, show_alert=True)
    
    # Видаляємо повідомлення з предметом
    await callback.message.delete()

# --- ЕКІПІРУВАННЯ ПРЕДМЕТУ (Зброя/Броня) ---
@inv_router.callback_query(F.data.startswith("equip_"))
async def equip(callback: types.CallbackQuery):
    inv_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # Перемикаємо статус
    result = db.toggle_equip_item(user_id, inv_id)
    
    await callback.answer(f"Предмет {result}!")
    
    # Видаляємо повідомлення
    await callback.message.delete()

# --- ЗАКРИТТЯ МЕНЮ ---
@inv_router.callback_query(F.data == "close_inv")
async def close(callback: types.CallbackQuery):
    await callback.message.delete()