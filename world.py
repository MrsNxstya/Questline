import sqlite3
from config import DB_NAME

def get_location_data(lid):
    """
    Отримує базові дані локації (текст, картинка) та можливі переходи.
    Використовується для генерації клавіатури в грі.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Отримуємо дані самої локації
    cur.execute("SELECT description, image_id FROM locations WHERE id=?", (lid,))
    res = cur.fetchone()
    txt, img = (res[0], res[1]) if res else ("Empty", None)
    
    # Отримуємо список кнопок (переходів)
    cur.execute("SELECT id, to_location_id, event_id, label FROM transitions WHERE from_location_id=?", (lid,))
    r = cur.fetchall()
    
    conn.close()
    return txt, img, r

def get_location_full(lid):
    """
    Отримує повну інформацію про локацію, включаючи назву та імена сусідніх локацій.
    Використовується для команди 'Карта'.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Отримуємо основні дані
    cur.execute("SELECT name, description, image_id FROM locations WHERE id=?", (lid,))
    res = cur.fetchone()
    
    if not res:
        conn.close()
        return "Unknown", "Empty", None, []
        
    name, txt, img = res
    
    # Отримуємо назви сусідніх локацій для навігації
    cur.execute('''
        SELECT t.label, l.name, t.to_location_id
        FROM transitions t
        LEFT JOIN locations l ON t.to_location_id = l.id
        WHERE t.from_location_id = ? AND t.to_location_id IS NOT NULL
    ''', (lid,))
    neighbors = cur.fetchall()
    
    conn.close()
    return name, txt, img, neighbors

def add_new_location(name, desc, img):
    """
    Створює нову локацію в базі даних.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO locations (name, description, image_id) VALUES (?,?,?)", (name, desc, img))
    nid = cur.lastrowid
    conn.commit()
    conn.close()
    return nid

def add_new_transition(f, t, l):
    """
    Створює перехід між двома локаціями.
    f (from): ID звідки
    t (to): ID куди
    l (label): Текст на кнопці
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO transitions (from_location_id, to_location_id, label) VALUES (?,?,?)", (f, t, l))
    conn.commit()
    conn.close()

def update_location(lid, description, image_id):
    """
    Оновлює опис або картинку існуючої локації.
    Якщо передано ".", поле не змінюється.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    if description != ".":
        cur.execute("UPDATE locations SET description = ? WHERE id = ?", (description, lid))
    
    if image_id != ".":
        cur.execute("UPDATE locations SET image_id = ? WHERE id = ?", (image_id, lid))
        
    conn.commit()
    conn.close()

def add_event(name, desc, chance, win_id, fail_id, img):
    """
    Створює нову подію (битву або ризиковану дію).
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (name, description, base_chance, win_location_id, fail_location_id, image_id) 
        VALUES (?,?,?,?,?,?)""", 
        (name, desc, chance, win_id, fail_id, img))
    nid = cur.lastrowid
    conn.commit()
    conn.close()
    return nid

def get_event(eid):
    """
    Отримує дані події за її ID.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM events WHERE id=?", (eid,))
    r = cur.fetchone()
    conn.close()
    return r

def add_event_transition(f, e, l):
    """
    Створює кнопку, яка веде не на іншу локацію, а запускає подію.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO transitions (from_location_id, event_id, label) VALUES (?,?,?)", (f, e, l))
    conn.commit()
    conn.close()