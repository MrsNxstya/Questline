from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard():
    """
    Створює головну клавіатуру (меню) для гравця.
    Кнопки відображаються під полем вводу тексту.
    """
    builder = ReplyKeyboardBuilder()
    
    # Додаємо кнопки
    builder.button(text="🎒 Інвентар")
    builder.button(text="👤 Статус")
    builder.button(text="📜 Квести")
    builder.button(text="🗺 Карта")
    
    # Налаштування сітки: 2 кнопки в першому ряду, 2 у другому
    builder.adjust(2, 2)
    
    # resize_keyboard=True робить кнопки компактними
    return builder.as_markup(resize_keyboard=True)