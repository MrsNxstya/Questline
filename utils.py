from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from io import BytesIO
from PIL import Image
from config import ADMIN_ID
from aiogram.types import BufferedInputFile
from aiogram.enums import ParseMode

utils_router = Router()

# --- МЕНЮ АДМІНА ---
@utils_router.message(Command("admin"))
async def cmd_admin_help(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(
        "🛠 **Панель Адміністратора**\n\n"
        "📍 **Світ:** /new_loc, /connect, /edit_loc\n"
        "⚔️ **Предмети:** /new_item, /edit_item, /give [ID]\n"
        "🤖 **AI:** /gen_loot [кількість]\n"
        "🎲 **Події:** /new_event, /link_event\n"
        "🖼 **Пікселізатор:** Просто кинь фото.",
        parse_mode=ParseMode.MARKDOWN
    )

# --- ПІКСЕЛІЗАТОР ---
@utils_router.message(F.photo)
async def pixelate(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    
    try:
        # 1. Завантажуємо файл
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        data = await message.bot.download_file(file.file_path)
        
        # 2. Обробка (Пікселізація)
        img = Image.open(data)
        
        # Зменшення розміру до 64x64 (створюємо пікселі)
        img_small = img.resize((64, 64), Image.Resampling.BILINEAR)
        # Збільшення до оригінального розміру (зберігаємо пікселі)
        res = img_small.resize(img.size, Image.Resampling.NEAREST)
        
        # 3. Зберігаємо в буфер
        out = BytesIO()
        res.save(out, format="PNG")
        out.seek(0)
        
        # 4. Відправляємо назад
        sent = await message.answer_photo(
            BufferedInputFile(out.read(), filename="pixel_art.png"),
            caption="👾 **ID цієї картинки:**"
        )
        # Виводимо ID для використання в адмін-командах
        await message.answer(f"`{sent.photo[-1].file_id}`")

    except Exception as e:
        await message.answer(f"❌ Помилка обробки фото: {e}")