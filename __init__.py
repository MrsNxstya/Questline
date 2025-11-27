from aiogram import Router

# Імпортуємо роутери з окремих файлів у цій папці
from .utils import utils_router
# from .locations import loc_router  # Removed add new location logic
from .items import items_router
from .events import events_router

# Створюємо головний роутер для Адмін-панелі
admin_router = Router()

# Підключаємо всі частини адмінки до головного роутера
admin_router.include_router(utils_router)
# admin_router.include_router(loc_router)  # Removed add new location logic
admin_router.include_router(items_router)
admin_router.include_router(events_router)
