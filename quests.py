# ai/quests.py

def get_quest_instruction(active_quests, has_main, goal):
    """
    Генерує розширені інструкції для AI щодо управління квестами.
    Розділяє логіку на Основний Сюжет та Побічні Активності.
    """
    
    # Якщо немає головного квесту - вмикаємо "сирену" для AI
    force_main_quest = ""
    if not has_main:
        force_main_quest = f"""
        🚨 **PRIORITY ALERT:** PLAYER HAS NO MAIN QUEST!
        You MUST create a new 'MAIN' quest immediately in the 'new_quest' field.
        This quest must be a step towards the Chapter Goal: "{goal}".
        """

    return f"""
    === 📜 ADVANCED QUEST SYSTEM ===
    
    CURRENT QUEST LOG:
    {active_quests}
    
    RULES FOR GENERATING TASKS:
    
    1. **MAIN QUESTS (The Storyline):**
       {force_main_quest}
       - Goal: Lead the player to the end of the current Chapter.
       - Nature: Mandatory, story-driven, serious.
       - Progression: If the player finishes one main task, give the next one until the Chapter Goal is reached.
       
    2. **SIDE QUESTS (The World & Relations):**
       - **Trigger:** Generate these when the player talks to NPCs, explores, or asks for work.
       - **Purpose:** To improve/worsen relationships, earn XP, or get Items.
       - **Variations:**
         * *Reputation Task:* "Deliver a letter for the Mayor" (+Reputation with City).
         * *Dirty Work:* "Steal from the merchant" (-Reputation, +Money).
         * *Grind/Loot:* "Kill 5 Wolves" (Reward: XP + Wolf Pelts).
       - **Choice:** These are optional. If the player refuses, the NPC might get offended.
       
    3. **COMPLETION LOGIC:**
       - If the player's action fulfills a quest condition, write the EXACT quest name in 'completed_quest_name'.
       - **Rewards:** Describe the reward in the story (e.g., "He hands you a sword", "You feel stronger"). The system will handle XP automatically.
    """