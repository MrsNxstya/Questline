from config import WORLD_HISTORY, MAGIC_SYSTEM, KINGDOMS_LORE

def get_combat_instruction(hp, max_hp, atk, defn, is_fighting):
    """
    Генерує інструкції для бойової системи.
    Враховує статус бою, здоров'я та ресурси.
    """
    status = "⚔️ COMBAT MODE" if is_fighting else "🕊️ EXPLORATION MODE"

    return f"""
    === {status} ===
    PLAYER STATS:
    - Health (HP): {hp}/{max_hp}
    - Attack Power (ATK): {atk}
    - Defense (DEF): {defn} (Note: The code automatically subtracts this from enemy damage).

    COMBAT RULES (DARK FANTASY):
    1. **STATUS CHANGE:**
       - If the player attacks an enemy or is attacked -> set "combat_status": "start".
       - If the fight ends (enemy dead, player ran away, diplomacy) -> set "combat_status": "end".
       - If the fight continues -> set "combat_status": "continue" (or leave null).

    2. **ENEMY ATTACK (DAMAGE):**
       - If the enemy hits the player, calculate the RAW damage (before armor).
       - Examples: Rat bite = 5, Bandit sword = 15, Dragon breath = 50.
       - Write this raw number in the "damage_taken" field.

    3. **PLAYER ATTACK:**
       - Compare the Player's ATK ({atk}) vs the Enemy's toughness.
       - Describe the impact vividly based on the stats.

    4. **RESOURCE USAGE (MP/SP):**
       - If the player uses a Spell/Magic -> set "spend_mp": amount (e.g. 20).
       - If the player uses a Heavy Attack/Sprint/Dodge -> set "spend_sp": amount (e.g. 10).

    5. **LOOT (VICTORY ONLY):**
       - If the player WINS the battle, determine the difficulty of the enemy (1-5).
       - 1=Easy (Rat), 3=Medium (Knight), 5=Boss (Dragon).
       - Write this number in "loot_difficulty".
    """

def get_world_context(chapter, lore, party, rep):
    """
    Генерує контекст світу, включаючи поточну главу, репутацію та глобальний лор.
    """
    # Визначаємо текстовий статус репутації для AI
    rep_bar = "NEUTRAL"
    if rep >= 50: rep_bar = "HERO (Everyone loves you)"
    elif rep >= 20: rep_bar = "RESPECTED (People are friendly)"
    elif rep <= -50: rep_bar = "VILLAIN (Everyone hates/fears you)"
    elif rep <= -20: rep_bar = "DISLIKED (People are suspicious)"

    return f"""
    === 🌍 DARK FANTASY WORLD CONTEXT ===
    GLOBAL HISTORY: {WORLD_HISTORY}
    MAGIC RULES: {MAGIC_SYSTEM}

    CURRENT CHAPTER: {chapter}
    LOCATION LORE: {lore}

    PLAYER REPUTATION: {rep} ({rep_bar})
    - NPCs must react according to this reputation!
    - Heroes get discounts and secrets. Villains get threats and bad prices.

    CURRENT PARTY (COMPANIONS):
    {party}
    """

def get_map_context(chapter_num, lore):
    """
    Extracts current location from chapter lore and provides map-based description for AI.
    """
    # Extract location from lore
    location = "Unknown"
    if "CURRENT LOCATION:" in lore:
        loc_line = lore.split("CURRENT LOCATION:")[1].split("\n")[0].strip()
        # Extract kingdom name, e.g., "Border of Hilinguard Kingdom" -> "Hilinguard"
        if "Hilinguard" in loc_line:
            location = "Hilinguard"
        elif "Windfoldigan" in loc_line:
            location = "Windfoldigan"
        # Add more as needed

    # Get description from KINGDOMS_LORE
    desc = ""
    for line in KINGDOMS_LORE.split("\n"):
        if location.upper() in line.upper() and ":" in line:
            desc = line.split(":", 1)[1].strip()
            break

    return f"""
    === 🗺 MAP CONTEXT ===
    CURRENT LOCATION: {location}
    DESCRIPTION: {desc}
    - Always describe the surroundings based on this lore in your responses.
    - Use sensory details: atmosphere, dangers, status.
    """

def get_puzzle_instructions():
    """
    Provides AI instructions to embed text-based mini-games or puzzles in narrative responses.
    Use special JSON fields to track puzzle state, player progress, and outcomes.
    """
    return """
    === MINI-GAMES & PUZZLES IN NARRATIVE RESPONSES ===
    1. Embed interactive puzzles or mini-games into storytelling where players must solve or interact.
    2. Use special keys in the JSON response for puzzle state management:
       - "puzzle_active": true/false
       - "puzzle_description": string describing the puzzle or hint
       - "puzzle_state": JSON object representing current puzzle progress/details
       - "puzzle_options": list of choices player can make for the puzzle
       - "puzzle_result": string describing outcome for last puzzle action
    3. Ensure players can attempt, fail, or succeed with consequences reflected in puzzles and story.
    4. Keep puzzle state updated each turn to maintain continuity.
    """

def get_emotional_logic():
    """
    Додаткові інструкції для відіграшу емоцій та наслідків.
    Включає логіку побічних квестів (Idea 7) та чіткі емоції (Idea 6).
    """
    return """
    === 🎭 EMOTIONAL INTELLIGENCE & CONSEQUENCES ===
    1. **NPC REACTION:** - Do not just state emotions ("He is angry"). Show them through dialogue and actions.
       - React to the player's tone and reputation.

    2. **SIDE QUEST CONSEQUENCES (REPUTATION):**
       - **GOOD DEEDS:** If the player accepts/completes a noble Side Quest (helping, saving) -> set "reputation_change": +5 (or more).
       - **BAD DEEDS:** If the player accepts/completes an evil Side Quest (stealing, killing innocents) -> set "reputation_change": -10 (or more).
       - **REFUSAL:** If the player refuses a request rudely -> NPC gets Angry ("npc_mood").

    3. **ATMOSPHERE & TONE:** - Adapt the narration tone to the current 'npc_mood' and situation (Gritty, Mysterious, Tense).
       - Describe sensory details (smell of rain, cold wind).

    4. **EXP EARNING LOGIC:**
       - **SIMPLE TALK:** After basic conversations with NPCs, grant small EXP (5-15) to encourage exploration.
       - **DISCOVERIES:** Finding new locations, items, or secrets -> 10-25 EXP.
       - **QUEST PROGRESS:** Accepting quests -> 20-50 EXP, completing -> 50-200 EXP based on difficulty.
       - **COMBAT:** Winning fights -> 20-100 EXP based on enemy difficulty.
       - **RARELY NO EXP:** Only in cases of failure, rudeness, or repeated actions without progress.
       - Always include "exp_gained" in JSON for meaningful interactions.
    """

def get_branching_dialogue_instructions(party_personalities):
    """
    Provides AI instructions to create branching dialogues influenced by player reputation, companions, and past player decisions.
    Includes companion personality descriptions to influence dialogue options.
    """
    personalities_text = ", ".join([f"{p['name']}({p['personality']})" for p in party_personalities]) if party_personalities else "No companions"
    return f"""
    === BRANCHING DIALOGUE & STORY PATHS ===
    1. Adjust dialogue options and story outcomes based on player reputation and past choices.
    2. Reflect companion personalities in dialogue, offering unique perspectives or influencing player choices.
    3. Present meaningful consequences for each choice.
    4. Party Companions currently present: {personalities_text}
    5. **STICK TO LORE:** Always adhere to the DARK FANTASY world described in config.py. Do not introduce modern elements, technology, or break immersion. Keep responses within the MMO RPG framework - no wandering off-topic.
    6. **WORLD BOUNDARIES:** Respect the world boundaries in config.py. Prevent players from leaving the map by describing natural barriers. You can create sub-locations, villages, towns, or specific sites within the existing kingdoms (Hilinguard, Stormfallen, Forestfall, Windfoldigan, Winterfall, Oceanrise, Heathergan, Liddingal), but NEVER create new kingdoms, continents, or locations outside the defined map. If players try to travel beyond the map, redirect them back with natural barriers like oceans, mountains, or guards.
    """

def get_dynamic_npc_mood(reputation: int, previous_mood: str = "") -> str:
    """
    Generates a dynamic NPC mood description string based on player's reputation and previous NPC mood.
    This mood will influence AI dialogue and responses.
    """
    mood = previous_mood
    # Define mood change logic based on reputation thresholds and prior mood
    if reputation >= 50:
        base_mood = "Friendly and supportive"
    elif reputation >= 20:
        base_mood = "Cautiously optimistic"
    elif reputation <= -50:
        base_mood = "Hostile and distrustful"
    elif reputation <= -20:
        base_mood = "Suspicious and wary"
    else:
        base_mood = "Neutral and reserved"

    # Slight random or context-based mood shift could be added here
    # For simplicity, we keep base mood or escalate mood if previous was more extreme

    # Example escalation logic
    extremes = ["Hostile and distrustful", "Friendly and supportive"]
    if previous_mood in extremes and previous_mood != base_mood:
        mood = previous_mood
    else:
        mood = base_mood

    return f"NPC mood: {mood}"

def get_json_format():
    """
    Повертає суворий формат JSON.
    """
    return """
    === RESPONSE FORMAT (VALID JSON ONLY) ===
    You must reply with a single valid JSON object. Do not add markdown formatting outside the JSON.
    {
        "text": "Atmospheric story narration in Ukrainian...",
        "npc_mood": "Current Emotion (e.g. Angry, Happy, Neutral, Scared, Grateful)",
        "options": ["Short Action 1", "Short Action 2", "Short Action 3"],

        "damage_taken": number (0 if safe, >0 if hurt - raw damage before armor),
        "reputation_change": number (e.g. +5, -10, 0),
        "spend_mp": number (0 or cost of magic),
        "spend_sp": number (0 or cost of exertion),

        "combat_status": "start/continue/end/null",
        "loot_difficulty": number (0 if no loot, 1-5 if victory),

        "new_quest": {
            "name": "Quest Name",
            "type": "MAIN" or "SIDE",
            "xp": 100
        } (OR null),

        "completed_quest_name": "Exact Name from Log" (OR null),
        "add_companion": { "name": "Name", "race": "Race", "personality": "Desc" } (OR null),
        "chapter_complete": boolean (true only if chapter goal achieved)
    }
    """
