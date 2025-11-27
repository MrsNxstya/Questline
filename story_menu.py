from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db

async def show_story_menu(message: types.Message):
    """
    Показує меню історії з текстом лору та кнопками Нової/Продовження історії.
    """
    # Перевіряємо, чи є історія AI (чи гра вже почата)
    history = db.get_ai_history(message.from_user.id)
    has_story = bool(history.strip())

    # Створюємо меню для історії
    builder = InlineKeyboardBuilder()
    
    # Кнопка Нова Гра
    # (У новій версії ми хочемо, щоб вона відкривала Web App, але якщо це старий варіант - залишаємо callback)
    # Якщо ми використовуємо Web App для створення героя, то тут має бути посилання на Web App.
    # Але для простоти, нехай це меню поки що використовує callback, а в navigation.py ми це обробимо.
    
    builder.button(text="📜 Почати Нову Історію", callback_data="start_story_new")
    
    if has_story:
        builder.button(text="▶️ Продовжити", callback_data="start_story_continue")
    
    builder.adjust(1)

    lore_text = """
🌍 **DARK FANTASY WORLD: THE AGE OF ASHES**

Five hundred years ago, the "Shattering" occurred. The sky turned violet, and the gods went silent.
Magic became unstable and dangerous. Using it draws upon the user's life force (or sanity).
The world is divided into two massive continents: FAR LANDS (The Old World) and WINTERQUARD (The Frozen Hell).

**CURRENT STATE:** Civilization is crumbling. Roads are unsafe. Monsters from the Abyss roam freely at night.
People are suspicious, superstitious, and grim. Trust is the most expensive currency.

**YOUR JOURNEY BEGINS NOW...**
    """

    await message.answer(f"{lore_text}\n\n🏰 **Choose an option:**", reply_markup=builder.as_markup())