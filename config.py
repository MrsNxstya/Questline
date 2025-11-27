# config.py

# --- ТВОЇ КЛЮЧІ ---
GOOGLE_API_KEY = "AIzaSyAVAAJjR0j_wnUGPFTSbfqBfWvnJsDTXyg" 
API_TOKEN = '8271877189:AAF-uWO5vB2WdfwDx5_5Fzyyyhfx8yAc5u8'
ADMIN_ID = 863085352
DB_NAME = 'game_engine.db'

FAR_LANDS_START_ID = 2
GLOBAL_MAP_ID = "AgACAgIAAxkDAAICUmkl9vlbuj7HUzYJMtWvvBNyi6VSAAKMDWsb_BMwSZZb49xoWdq8AQADAgADeQADNgQ"

# --- НАЛАШТУВАННЯ RPG ---
RPG_RACES = {
    "🧝 Ельф": { "desc": "Магія та ліс. (+Мана)", "image": None },
    "🧔 Дворф": { "desc": "Гори та золото. (+Здоров'я)", "image": None },
    "👤 Людина": { "desc": "Універсальність. (+Харизма)", "image": None }
}

RPG_CLASSES = { 
    "⚔️ Воїн": "Сила та захист", 
    "🔮 Маг": "Заклинання та знання", 
    "🗡 Злодій": "Спритність та крадіжки" 
}

RPG_GENDERS = { "Male": "Чоловік", "Female": "Жінка" }

RPG_RARITY = { 
    "Common": "⚪ Звичайний", 
    "Rare": "🔵 Рідкісний", 
    "Epic": "🟣 Епічний", 
    "Legendary": "🟠 Легендарний" 
}

ITEM_TYPES = ["Weapon", "Armor", "Spell", "Item", "Artifact", "Potion", "Food"]

# --- ГЛОБАЛЬНА ІСТОРІЯ (DARK FANTASY LORE) ---
WORLD_HISTORY = """
THE AGE OF ASHES:
Five hundred years ago, the "Shattering" occurred. The sky turned violet, and the gods went silent.
Magic became unstable and dangerous. Using it draws upon the user's life force (or sanity).
The world is divided into two massive continents: FAR LANDS (The Old World) and WINTERQUARD (The Frozen Hell).

THE CURRENT STATE:
Civilization is crumbling. Roads are unsafe. Monsters from the Abyss roam freely at night.
People are suspicious, superstitious, and grim. Trust is the most expensive currency.
"""

MAGIC_SYSTEM = """
MAGIC RULES (The Ether):
1. Magic is not free. It requires "Ether" or blood.
2. Mages are feared and often hunted by the "Inquisition of Silence".
3. Healing magic is extremely rare and painful. Potions taste like ash.
"""

# --- ГЕОГРАФІЯ (8 КОРОЛІВСТВ) ---
KINGDOMS_LORE = """
FAR LANDS (Western side):
1. HILINGUARD (The Last Bastion):
   - Location: South-Eastern side of Far Lands, on a hill rise, next to the bridge to Winterquard, has way out to the ocean and docks.
   - Atmosphere: Rain, gray stone walls, mud, poverty mixed with fading nobility.
   - Status: Under martial law. The Gates are closed to non-citizens.
   - Danger: Corrupt guards, thieves guilds, plague in the slums.
   - Weather: Normal, sometimes raining, rarely snowing.
   - Races: Humans, Elves.
   - Rules: Kind, neutral to strangers.

2. STORMFALLEN (The Cursed Coast):
   - Location: North-Western side of Far Lands, center of trading and merchant sells.
   - Atmosphere: Perpetual thunderstorms, dark magic, necromancy.
   - Danger: Undead sailors, lightning strikes, cultists.
   - Weather: Stormy, frequent thunderstorms.
   - Races: Dwarfs, Gnomes, Goblins.
   - Rules: Neutral, skeptical (need to earn trust).

3. FORESTFALL (The Forest Depths):
   - Location: South-Western side of Far Lands.
   - Atmosphere: Dense forests, ancient trees, hidden groves.
   - Danger: Wild beasts, forest spirits, poisonous plants.
   - Weather: Humid, foggy, occasional rain.
   - Races: Orcs, Forest Elves.
   - Rules: Unkind, skeptical (need to earn trust; one fight, kill attempt, or steal - instant attack or expulsion).

WINTERQUARD (Eastern side):
4. WINDFOLDIGAN (The Howling Plains):
   - Location: North-Western side of Winterquard, attached with mountains to the South, always snowing.
   - Atmosphere: Endless winds that drive men mad. Nomadic tribes.
   - Danger: Wind spirits, giant beasts, scarcity of water.
   - Weather: Constant snow, freezing winds.
   - Races: Nords, Humans, Dwarfs.
   - Rules: Neutral, skeptical (need to earn trust).

5. WINTERFALL (The Cold Watch):
   - Location: South-Eastern side of Winterquard, near forest, has way out to the ocean.
   - Atmosphere: Snow, ice, hardened warriors. The border with Winterquard.
   - Danger: Frostbite, white walkers, scarcity of food.
   - Weather: Perpetual winter, requires warm clothes.
   - Races: Dwarfs, Humans, Nords, some Elves.
   - Rules: Neutral, skeptical (need to earn trust).

ISLANDS:
MIDDLE ISLAND TO THE SOUTH (Between Far Lands and Winterquard):
6. OCEANRISE (The Trade Jewel):
   - Location: Sand island in the middle, center of armor and rare weapons, good smiths.
   - Atmosphere: Foggy ports, black markets, smells of salt and fish.
   - Danger: Sea monsters, pirates, slavers.
   - Weather: Warmest part, requires lots of water or undressing.
   - Races: Cat-Humans.
   - Rules: Neutral (will attack back if you steal or kill).

NORTHERN ISLAND:
7. HEATHERGAN (The Witchlands):
   - Location: North island, between forest and winter lands, middle of the island, big mountains to the North.
   - Atmosphere: Purple heather fields hiding deep swamps. Hallucinogenic fog.
   - Danger: Witches, poisonous plants, illusions.
   - Weather: Misty, hallucinogenic.
   - Races: Elves, High Elves, Forest Elves.
   - Rules: Dangerous, unkind (requires trust, rarely attacks strangers).

SOUTH-EASTERN ISLAND:
8. LIDDINGAL (The Forgotten Isle):
   - Location: Small island on South-Eastern side of Winterquard, winter forever, hard to reach by boat or swimming.
   - Atmosphere: Isolated, strange architecture, alien flora.
   - Danger: Unknown ancient technology, madness, extreme cold.
   - Weather: Eternal winter, impossible without winter clothes.
   - Races: Nords, Giants.
   - Rules: Unkind, dangerous (trust earning difficult).

GEOGRAPHY OVERVIEW:
- Far Lands: Big sea in the middle, small seas and lakes to West and North. One big mountain beside the central sea (Western side), another to North and East.
- Winterquard: Big mountains to South, away from Windfoldigan. Heathergan island has mountains to North.
- Connections: Bridge between Far Lands and Winterquard (South-Eastern, beside Hilinguard). Bridge from Winterquard to Heathergan island (middle, North-Western). Heathergan connects to Oceanrise (South, middle).
- Surroundings: All lands surrounded by water; escaping the map leads to drowning.
- Weather: Far Lands normal (rainy, rarely snowy near borders). Winterquard always cold. Oceanrise warmest.
"""

# --- МЕЖІ СВІТУ ---
WORLD_BOUNDARIES = """
BOUNDARIES & LIMITS:
1. **Endless Ocean:** Surrounds the continents. Player cannot swim across without a ship.
2. **The Void Edge:** Does not exist. The world is round but limited by the map.
3. **Impassable Mountains:** North of Mountainfall. Too high to climb without special gear.
4. **The Frozen Wastes:** Deep Winterquard. Lethal cold kills anyone without magic protection.

IF PLAYER TRIES TO LEAVE THE MAP:
- Describe a natural barrier (storm, cliff, guards, endless ocean).
- Gently force them back to the playable area.
"""

# --- УНІКАЛЬНІ СУПУТНИКИ ---
UNIQUE_COMPANIONS = """
1. NAME: Kaelen "The Rat" (Human Thief). 
   - PERSONALITY: Sarcastic, loves gold, cowardly but useful. 
   - ENCOUNTER: Found in cages/prisons or tied up by bandits.
   - SPECIALTY: Can open locked doors and chests.

2. NAME: Borig Stone-Eater (Dwarf Outcast). 
   - PERSONALITY: Strong, dumb, speaks in third person, eats rocks. 
   - ENCOUNTER: Found fighting alone against many enemies.
   - SPECIALTY: Tanks damage, breaks heavy obstacles.

3. NAME: Lyra of the Mist (Elf Medium). 
   - PERSONALITY: Mysterious, whispers to ghosts, afraid of fire. 
   - ENCOUNTER: Found near graveyards, shrines or magical anomalies at night.
   - SPECIALTY: Heals the player, senses danger/magic.
"""

# --- СЮЖЕТ ГРИ (ГЛАВИ) ---
STORY_CHAPTERS = {
    1: {
        "title": "Глава 1: Попіл та Бруд",
        "lore": f"""
        {WORLD_HISTORY}
        {KINGDOMS_LORE}
        {WORLD_BOUNDARIES}

        CURRENT LOCATION: Border of Hilinguard Kingdom. The muddy road before the Great Gates.

        PLAYER SITUATION (START):
        The player was a wealthy traveler. Just an hour ago, bandits ambushed them.
        Current Status: Robbed completely. Woke up dizzy in the mud. No weapon, no money, no horse. Only ragged clothes remain.
        Health is low due to the beating.

        GOAL: Get inside the city of Hilinguard to find shelter and help.
        OBSTACLES: The guards require an entry fee or a pass (which was stolen).

        POTENTIAL COMPANIONS NEARBY:
        {UNIQUE_COMPANIONS}
        """,
        "objectives": [
            "1. Recover senses and find a basic item (stick, stone, rusty knife).",
            "2. Find food or water to restore strength.",
            "3. Pass the Gate Guards (bribe/sneak/persuade/climb).",
            "4. Enter Hilinguard City."
        ],
        "next_chapter_id": 2
    },
    2: {
        "title": "Глава 2: Тіні Хілінгарду",
        "lore": f"""
        {KINGDOMS_LORE}
        CURRENT LOCATION: Hilinguard Outer District (The Slums).
        ATMOSPHERE: Despair, crime, dark alleyways.
        GOAL: Survive the first night and find information about the bandits who robbed you.
        """,
        "objectives": [
            "1. Find money for a bed or sleep on the street.",
            "2. Visit the local tavern 'The Broken Wheel'.",
            "3. Meet a contact who saw the bandits."
        ],
        "next_chapter_id": 3
    }
}

# --- КАРТА СВІТУ ---
MAP_LOCATIONS = {
    "Hilinguard": {
        "desc": "The Last Bastion: South-Eastern Far Lands, on a hill rise, next to the bridge to Winterquard. Rain, gray stone walls, mud, poverty mixed with fading nobility. Under martial law. Gates closed to non-citizens. Danger: Corrupt guards, thieves guilds, plague in the slums.",
        "adjacent": ["Winterfall", "Stormfallen", "Forestfall"]
    },
    "Stormfallen": {
        "desc": "The Cursed Coast: North-Western Far Lands, center of trading and merchant sells. Perpetual thunderstorms, dark magic, necromancy. Danger: Undead sailors, lightning strikes, cultists.",
        "adjacent": ["Hilinguard", "Forestfall"]
    },
    "Forestfall": {
        "desc": "The Forest Depths: South-Western Far Lands. Dense forests, ancient trees, hidden groves. Danger: Wild beasts, forest spirits, poisonous plants.",
        "adjacent": ["Hilinguard", "Stormfallen", "Oceanrise"]
    },
    "Windfoldigan": {
        "desc": "The Howling Plains: North-Western Winterquard, attached with mountains to the South, always snowing. Endless winds that drive men mad. Nomadic tribes. Danger: Wind spirits, giant beasts, scarcity of water.",
        "adjacent": ["Winterfall", "Heathergan"]
    },
    "Winterfall": {
        "desc": "The Cold Watch: South-Eastern Winterquard, near forest, has way out to the ocean. Snow, ice, hardened warriors. The border with Winterquard. Danger: Frostbite, white walkers, scarcity of food.",
        "adjacent": ["Hilinguard", "Windfoldigan", "Liddingal"]
    },
    "Oceanrise": {
        "desc": "The Trade Jewel: Sand island in the middle, center of armor and rare weapons, good smiths. Foggy ports, black markets, smells of salt and fish. Danger: Sea monsters, pirates, slavers.",
        "adjacent": ["Forestfall", "Heathergan"]
    },
    "Heathergan": {
        "desc": "The Witchlands: North island, between forest and winter lands, middle of the island, big mountains to the North. Purple heather fields hiding deep swamps. Hallucinogenic fog. Danger: Witches, poisonous plants, illusions.",
        "adjacent": ["Windfoldigan", "Oceanrise", "Liddingal"]
    },
    "Liddingal": {
        "desc": "The Forgotten Isle: Small island on South-Eastern side of Winterquard, winter forever, hard to reach by boat or swimming. Isolated, strange architecture, alien flora. Danger: Unknown ancient technology, madness, extreme cold.",
        "adjacent": ["Winterfall", "Heathergan"]
    }
}