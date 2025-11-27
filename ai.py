import sqlite3
from config import DB_NAME

def get_ai_history(user_id):
    """Отримує історію діалогу користувача з AI."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT history FROM ai_memory WHERE user_id = ?", (user_id,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else ""

def update_ai_history(user_id, new_text):
    """Оновлює історію діалогу, додаючи новий текст."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT history FROM ai_memory WHERE user_id = ?", (user_id,))
    res = cur.fetchone()
    
    if res:
        # Додаємо новий текст до старого, обрізаючи до останніх 6000 символів
        hist = (res[0] + "\n" + new_text)[-6000:]
        conn.execute("UPDATE ai_memory SET history = ? WHERE user_id = ?", (hist, user_id))
    else:
        # Створюємо новий запис, якщо історії ще немає
        conn.execute("INSERT INTO ai_memory (user_id, history) VALUES (?, ?)", (user_id, new_text))
    
    conn.commit()
    conn.close()

def clear_ai_history(user_id):
    """Очищає історію діалогу (наприклад, при початку нової глави)."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM ai_memory WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_companion(user_id, name, race, personality):
    """Додає нового супутника в команду гравця."""
    conn = sqlite3.connect(DB_NAME)
    # Перевіряємо, чи цей супутник вже є активним, щоб не дублювати
    cur = conn.cursor()
    cur.execute("SELECT id FROM companions WHERE user_id=? AND name=? AND status='active'", (user_id, name))
    if not cur.fetchone():
        conn.execute("INSERT INTO companions (user_id, name, race, personality) VALUES (?,?,?,?)", (user_id, name, race, personality))
        conn.commit()
    conn.close()

def get_active_companions_text(user_id):
    """Повертає текстовий список активних супутників для передачі в AI."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name FROM companions WHERE user_id=? AND status='active'", (user_id,))
    rows = cur.fetchall()
    conn.close()
    
    if rows:
        return ", ".join([row[0] for row in rows])
    else:
        return "None (Player is alone)."

def get_active_companions_with_personality(user_id):
    """Return a list of dicts with active companions' name and personality."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name, personality FROM companions WHERE user_id=? AND status='active'", (user_id,))
    rows = cur.fetchall()
    conn.close()
    
    companions = []
    for row in rows:
        companions.append({"name": row[0], "personality": row[1] if row[1] else "Unknown"})
    return companions


# --- New: Event statistics tracking ---

def initialize_statistics_table():
    """Create event_statistics table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS event_statistics (
            user_id INTEGER PRIMARY KEY,
            fight_count INTEGER DEFAULT 0,
            steal_count INTEGER DEFAULT 0,
            bribe_count INTEGER DEFAULT 0,
            talk_count INTEGER DEFAULT 0,
            explore_count INTEGER DEFAULT 0,
            quest_accept_count INTEGER DEFAULT 0,
            quest_complete_count INTEGER DEFAULT 0,
            other_event_count INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()

def increment_statistic(user_id, event_type):
    """Increment the count for a specific event type for the user."""
    initialize_statistics_table()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM event_statistics WHERE user_id = ?", (user_id,))
    exists = cur.fetchone()
    
    if not exists:
        conn.execute("""
            INSERT INTO event_statistics
            (user_id, fight_count, steal_count, bribe_count, talk_count, explore_count, quest_accept_count, quest_complete_count, other_event_count)
            VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0);
        """, (user_id,))
        conn.commit()

    column = {
        "fight": "fight_count",
        "steal": "steal_count",
        "bribe": "bribe_count",
        "talk": "talk_count",
        "explore": "explore_count",
        "quest_accept": "quest_accept_count",
        "quest_complete": "quest_complete_count"
    }.get(event_type, "other_event_count")
    
    conn.execute(f"""
        UPDATE event_statistics
        SET {column} = {column} + 1
        WHERE user_id = ?;
    """, (user_id,))
    conn.commit()
    conn.close()

def get_statistics_summary(user_id):
    """Get player's event statistics summary string."""
    initialize_statistics_table()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT fight_count, steal_count, bribe_count, talk_count, explore_count, quest_accept_count, quest_complete_count, other_event_count
        FROM event_statistics
        WHERE user_id = ?;
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return "Статистика подій поки відсутня."

    fight, steal, bribe, talk, explore, quest_accept, quest_complete, other = row

    return (
        f"📊 **Статистика Подій:**\n"
        f"⚔️ Битви: {fight}\n"
        f"🗝 Крадіжки: {steal}\n"
        f"💰 Хабарі: {bribe}\n"
        f"💬 Розмови: {talk}\n"
        f"🗺 Дослідження: {explore}\n"
        f"📜 Прийняті квести: {quest_accept}\n"
        f"✅ Виконані квести: {quest_complete}\n"
        f"❓ Інші події: {other}"
    )


# NPC Mood persistent storage functions

def initialize_npc_mood_table():
    """Create npc_moods table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS npc_moods (
        user_id INTEGER PRIMARY KEY,
        mood TEXT DEFAULT ""
    );
    """)
    conn.commit()
    conn.close()

def get_npc_mood(user_id):
    """Retrieve the stored npc_mood string for the user."""
    initialize_npc_mood_table()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT mood FROM npc_moods WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return ""

def set_npc_mood(user_id, mood):
    """Stores the npc_mood string for the user."""
    initialize_npc_mood_table()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM npc_moods WHERE user_id=?", (user_id,))
    exists = cur.fetchone()
    if exists:
        conn.execute("UPDATE npc_moods SET mood=? WHERE user_id=?", (mood, user_id))
    else:
        conn.execute("INSERT INTO npc_moods (user_id, mood) VALUES (?, ?)", (user_id, mood))
    conn.commit()
    conn.close()

def initialize_puzzle_state_table():
    """Create puzzle_states table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS puzzle_states (
        user_id INTEGER PRIMARY KEY,
        puzzle_state TEXT DEFAULT '{}'
    );
    """)
    conn.commit()
    conn.close()

def get_puzzle_state(user_id):
    """Retrieve the stored puzzle_state JSON string for the user."""
    initialize_puzzle_state_table()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT puzzle_state FROM puzzle_states WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    else:
        return "{}"

def set_puzzle_state(user_id, puzzle_state_json_str):
    """Store the puzzle_state JSON string for the user."""
    initialize_puzzle_state_table()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM puzzle_states WHERE user_id=?", (user_id,))
    exists = cur.fetchone()
    if exists:
        conn.execute("UPDATE puzzle_states SET puzzle_state=? WHERE user_id=?", (puzzle_state_json_str, user_id))
    else:
        conn.execute("INSERT INTO puzzle_states (user_id, puzzle_state) VALUES (?, ?)", (user_id, puzzle_state_json_str))
    conn.commit()
    conn.close()
