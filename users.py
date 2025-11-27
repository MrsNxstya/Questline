import sqlite3
import time
from config import DB_NAME

def get_full_player_stats(user_id):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    # Запит, що вимагає всі колонки
    cur.execute("""SELECT race, gender, age, char_class, level, xp, hp, max_hp, mp, max_mp, sp, max_sp, is_fighting, reputation FROM users WHERE user_id=?""", (user_id,))
    res = cur.fetchone(); conn.close(); return res

def get_user_info(uid):
    conn = sqlite3.connect(DB_NAME)
    res = conn.execute("SELECT current_location_id, race, gender, age, char_class FROM users WHERE user_id=?",(uid,)).fetchone()
    if not res: 
        conn.close()
        return ("Unknown Place", "-", "-", 0, "-")
    
    loc_id = res[0]
    loc_res = conn.execute("SELECT name FROM locations WHERE id=?", (loc_id,)).fetchone()
    loc_name = loc_res[0] if loc_res else "Unknown Place"
    
    conn.close()
    return (loc_name, res[1], res[2], res[3], res[4])

def save_character_data(uid, r, g, a, c):
    conn = sqlite3.connect(DB_NAME)
    now = int(time.time())
    conn.execute("UPDATE users SET race=?, gender=?, age=?, char_class=?, last_active=?, hp=100, max_hp=100, reputation=0 WHERE user_id=?", (r,g,a,c,now,uid))
    conn.commit(); conn.close()

def update_user_location(uid, lid):
    conn = sqlite3.connect(DB_NAME)
    exists = conn.execute("SELECT user_id FROM users WHERE user_id=?", (uid,)).fetchone()
    if exists:
        conn.execute("UPDATE users SET current_location_id=?, is_fighting=0 WHERE user_id=?", (lid, uid))
    else:
        conn.execute("INSERT INTO users (user_id, current_location_id, is_fighting) VALUES (?,?,0)", (uid, lid))
    conn.commit(); conn.close()

def change_reputation(user_id, amount):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT reputation FROM users WHERE user_id=?", (user_id,)); res = cur.fetchone()
    curr = res[0] if res else 0
    new_rep = max(-100, min(100, curr + amount))
    conn.execute("UPDATE users SET reputation=? WHERE user_id=?", (new_rep, user_id))
    conn.commit(); conn.close()
    status = "Neutral"
    if new_rep >= 50: status = "Hero"
    elif new_rep <= -50: status = "Villain"
    return new_rep, status

def spend_resource(user_id, res_type, amount):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    col = res_type.lower()
    if col not in ['hp', 'mp', 'sp']: conn.close(); return False
    cur.execute(f"SELECT {col} FROM users WHERE user_id=?", (user_id,))
    val = cur.fetchone()[0]
    if val >= amount:
        conn.execute(f"UPDATE users SET {col}=? WHERE user_id=?", (val - amount, user_id))
        conn.commit(); conn.close(); return True
    conn.close(); return False

def set_fighting_status(uid, status):
    conn = sqlite3.connect(DB_NAME); conn.execute("UPDATE users SET is_fighting=? WHERE user_id=?", (status, uid)); conn.commit(); conn.close()

def regenerate_stats(user_id):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT hp, max_hp, mp, max_mp, sp, max_sp, last_active, is_fighting FROM users WHERE user_id=?", (user_id,))
    data = cur.fetchone()
    if not data: conn.close(); return
    hp, mhp, mp, mmp, sp, msp, last, fight = data
    if not last: last = int(time.time())
    now = int(time.time()); diff = now - last
    if diff < 10: conn.close(); return
    
    rhp, rmp, rsp = 0, 0, 0
    if not fight:
        rhp = int(diff/60)*5; rmp = int(diff/15)*2; rsp = int(diff/10)*5
    
    conn.execute("UPDATE users SET hp=MIN(?,?), mp=MIN(?,?), sp=MIN(?,?), last_active=? WHERE user_id=?",
                (hp+rhp, mhp, mp+rmp, mmp, sp+rsp, msp, now, user_id))
    conn.commit(); conn.close()

def take_damage(user_id, raw):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT hp, max_hp FROM users WHERE user_id=?", (user_id,)); stats = cur.fetchone()
    if not stats: conn.close(); return "Error"
    hp, mhp = stats
    cur.execute('SELECT SUM(i.defense_bonus) FROM inventory inv JOIN items i ON inv.item_id = i.id WHERE inv.user_id=? AND inv.is_equipped=1', (user_id,))
    d = cur.fetchone()[0]; defense = d if d else 0
    actual = max(0, raw - defense)
    if raw > 0 and actual == 0 and defense < 100: actual = 1
    new_hp = max(0, hp - actual)
    conn.execute("UPDATE users SET hp=? WHERE user_id=?", (new_hp, user_id))
    conn.commit(); conn.close(); return f"💔 Урон: {actual} (Блок: {defense}). HP: {new_hp}/{mhp}"

def add_xp(user_id, amount):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT level, xp FROM users WHERE user_id=?", (user_id,)); res = cur.fetchone()
    if not res: conn.close(); return ""
    lvl, cxp = res; nxp = cxp + amount; msg = f"+{amount} XP"
    if nxp >= lvl*100 and lvl<100: lvl+=1; nxp-=lvl*100; msg+=f"\n🎉 **LEVEL UP!** {lvl}"
    conn.execute("UPDATE users SET level=?, xp=? WHERE user_id=?", (lvl, nxp, user_id)); conn.commit(); conn.close(); return msg