import sqlite3

def seed():
    conn = sqlite3.connect('game_engine.db')
    cursor = conn.cursor()

    # 1. Очищаємо таблиці (щоб не дублювати дані, якщо запустиш двічі)
    cursor.execute('DELETE FROM locations')
    cursor.execute('DELETE FROM transitions')
    cursor.execute('DELETE FROM users') # Скидаємо прогрес

    # 2. Додаємо ЛОКАЦІЇ
    # ID 1 - Вхід
    # ID 2 - Ліс
    # ID 3 - Озеро
    cursor.execute("INSERT INTO locations (id, description) VALUES (1, 'Ви стоїте біля входу в темну печеру. Ліворуч шумить ліс, праворуч виблискує озеро.')")
    cursor.execute("INSERT INTO locations (id, description) VALUES (2, 'Ви зайшли в густий ліс. Тут темно і страшно. Десь виє вовк.')")
    cursor.execute("INSERT INTO locations (id, description) VALUES (3, 'Ви вийшли до озера. Вода чиста і прохолодна. Можна відпочити.')")

    # 3. Додаємо ПЕРЕХОДИ (Кнопки)
    # З Входу (1) -> в Ліс (2)
    cursor.execute("INSERT INTO transitions (from_location_id, to_location_id, label) VALUES (1, 2, '🌲 Піти в ліс')")
    # З Входу (1) -> до Озера (3)
    cursor.execute("INSERT INTO transitions (from_location_id, to_location_id, label) VALUES (1, 3, '🌊 Піти до озера')")
    
    # З Лісу (2) -> назад до Входу (1)
    cursor.execute("INSERT INTO transitions (from_location_id, to_location_id, label) VALUES (2, 1, '🔙 Повернутися до печери')")
    
    # З Озера (3) -> назад до Входу (1)
    cursor.execute("INSERT INTO transitions (from_location_id, to_location_id, label) VALUES (3, 1, '🔙 Повернутися до печери')")

    conn.commit()
    conn.close()
    print("База даних успішно наповнена тестовим квестом!")

if __name__ == '__main__':
    seed()