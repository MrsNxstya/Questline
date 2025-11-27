from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import google.generativeai as genai
import json

from config import GOOGLE_API_KEY, STORY_CHAPTERS, UNIQUE_COMPANIONS
import database as db
from . import prompts, quests

# Глобальна змінна для збереження варіантів кнопок для кожного користувача
USER_OPTIONS = {}

class StoryMode(StatesGroup):
    active = State()

async def generate_ai_response(message: types.Message, state: FSMContext, prompt: str, uid: int):
    try:
        # 1. РЕГЕНЕРАЦІЯ СТАТИСТИКИ (Перед ходом)
        # Відновлюємо здоров'я, ману та стаміну, якщо пройшло достатньо часу
        db.regenerate_stats(uid)

        # 2. ЗБІР ДАНИХ З БАЗИ
        
        # Отримуємо поточну главу
        chapter_num = db.get_user_chapter(uid)
        chapter_data = STORY_CHAPTERS.get(chapter_num)
        
        if not chapter_data:
            await message.answer("🏁 Історія завершена! Дякуємо за гру.")
            return

        # Отримуємо активні квести та перевіряємо наявність головного сюжетного завдання
        quests_text = db.get_active_quests_text(uid)
        has_main_quest = db.has_main_quests(uid)

        # Отримуємо контекст карти для AI
        map_context = prompts.get_map_context(chapter_num, chapter_data.get('lore', ''))
        
        # Отримуємо повну статистику гравця
        res_stats = db.get_full_player_stats(uid)
        # Розпаковуємо кортеж:
        # 6:hp, 7:max_hp, 8:mp, 9:max_mp, 10:sp, 11:max_sp, 12:is_fighting, 13:reputation
        hp_curr, hp_max = res_stats[6], res_stats[7]
        mp_curr, mp_max = res_stats[8], res_stats[9]
        sp_curr, sp_max = res_stats[10], res_stats[11]
        is_fighting = res_stats[12]
        reputation = res_stats[13]

        # Отримуємо бойові характеристики (атака/захист від предметів)
        atk, defn = db.get_player_stats(uid)
        
        # Отримуємо список активних супутників
        party_text = db.get_active_companions_text(uid)
        
        # Визначаємо мову спілкування
        user_lang = message.from_user.language_code or "uk"

        # Get the previous NPC mood from database
        previous_mood = db.get_npc_mood(uid)

        # 3. НАЛАШТУВАННЯ AI (Gemini 2.5 Flash)
        genai.configure(api_key=GOOGLE_API_KEY)

        # Generate the current dynamic NPC mood string
        current_mood = prompts.get_dynamic_npc_mood(reputation, previous_mood)

        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config={"temperature": 0.9} # Зменшена креативність для кращої відповідності та швидкості
        )

        # 4. ФОРМУВАННЯ ПРОМПТА (Збираємо з модулів)
        companions_detail = db.get_active_companions_with_personality(uid)
        branching_instr = prompts.get_branching_dialogue_instructions(companions_detail)
        puzzle_instr = prompts.get_puzzle_instructions()
        current_puzzle_state_str = db.get_puzzle_state(uid)
        try:
            import json
            current_puzzle_state_json = json.loads(current_puzzle_state_str)
        except Exception:
            current_puzzle_state_json = {}
        instr = f"""
        ACT AS A DUNGEON MASTER. LANGUAGE: {user_lang}.
        POOL: {UNIQUE_COMPANIONS}
        RESOURCES: HP {hp_curr}/{hp_max}, MP {mp_curr}/{mp_max}, SP {sp_curr}/{sp_max}.
    
        {prompts.get_world_context(chapter_data['title'], chapter_data['lore'], party_text, reputation)}
    
        {branching_instr}
    
        {puzzle_instr}
    
        CURRENT PUZZLE STATE (JSON format):
        {json.dumps(current_puzzle_state_json, ensure_ascii=False, indent=2)}
    
        NPC MOOD CONTEXT:
        {current_mood}
    
        {prompts.get_combat_instruction(hp_curr, hp_max, atk, defn, is_fighting)}
    
        {quests.get_quest_instruction(quests_text, has_main_quest, chapter_data.get('objectives', 'Advance Plot'))}

        {prompts.get_emotional_logic()}

        LOCATION AWARENESS:
        - Always incorporate the current location description from MAP CONTEXT into your narrative.
        - Describe surroundings, atmosphere, and dangers vividly at the start of responses.
        - Use sensory details (sights, sounds, smells) to immerse the player in the location.

        {prompts.get_json_format()}
        """

        # Додаємо статус бою та дію гравця
        fight_status_txt = "COMBAT!" if is_fighting else "EXPLORATION."
        full_prompt = f"{instr}\n\nSTATUS: {fight_status_txt}\nUSER ACTION: {prompt}"

        # 5. ЗАПИТ ДО AI
        response = model.generate_content(full_prompt)

        # Чистка JSON від можливих markdown-тегів
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        # Чистка JSON від можливих markdown-тегів
        # Чистка JSON від можливих markdown-тегів

        # --- 6. ОБРОБКА ЛОГІКИ ГРИ ---
        
        system_msg = "" # Накопичувач системних повідомлень для виводу в кінці

        # А. Витрата ресурсів (MP/SP)
        mp_cost = data.get("spend_mp", 0)
        if mp_cost > 0:
            if db.spend_resource(uid, "mp", mp_cost):
                system_msg += f"🔹 -{mp_cost} MP\n"
            else:
                # Якщо мани не вистачає, перериваємо дію
                await message.answer("❌ Не вистачає мани для цієї дії!"); return

        sp_cost = data.get("spend_sp", 0)
        if sp_cost > 0:
            db.spend_resource(uid, "sp", sp_cost)
            system_msg += f"⚡ -{sp_cost} SP\n"
        
        # Б. Зміна репутації
        rep_change = data.get("reputation_change", 0)
        if rep_change != 0:
            new_rep, status_rep = db.change_reputation(uid, rep_change)
            sign = "+" if rep_change > 0 else ""
            system_msg += f"📈 Репутація: {sign}{rep_change} ({status_rep})\n"

        # В. Статус бою (Початок/Кінець)
        combat_status = data.get("combat_status")
        if combat_status == "start":
            db.set_fighting_status(uid, 1)
        elif combat_status == "end":
            db.set_fighting_status(uid, 0)

        # --- New: Puzzle state update handling ---
        try:
            puzzle_state_json = data.get("puzzle_state")
            if puzzle_state_json is not None:
                import json
                # Save updated puzzle state as JSON string
                puzzle_state_str = json.dumps(puzzle_state_json, ensure_ascii=False)
                db.set_puzzle_state(uid, puzzle_state_str)
        except Exception as e:
            print(f"Puzzle state update error: {e}")

        # --- New: Update event statistics ---
        try:
            # Detect event type with more keys

            event_type = "other"

            combat_starts = ["start", "begin"]
            combat_ends = ["end", "finish", "complete"]

            if combat_status in combat_starts + combat_ends:
                event_type = "fight"
            elif any(data.get(k) for k in ["steal_success", "steal_attempt", "steal"]):
                event_type = "steal"
            elif any(data.get(k) for k in ["bribe_success", "bribe_attempt", "bribe"]):
                event_type = "bribe"
            elif any(data.get(k) for k in ["simple_talk", "talk", "negotiate", "conversation"]):
                event_type = "talk"
            elif any(data.get(k) for k in ["quest_accept", "quest_start"]):
                event_type = "other"
            elif any(data.get(k) for k in ["quest_complete", "quest_done"]):
                event_type = "other"
            elif any(data.get(k) for k in ["explore", "discover"]):
                event_type = "other"
            # Add other event keys as needed

            # Increment statistics
            db.increment_statistic(uid, event_type)
            # After fight end, steal, bribe, talk, display stats summary
            if combat_status in combat_ends or event_type in ["steal", "bribe", "talk"]:
                stats_summary = db.get_statistics_summary(uid)
                if stats_summary:
                    system_msg += f"\n\n{stats_summary}"
        except Exception as e:
            print(f"Stats update error: {e}")

        # Г. Отримання урону
        damage_val = data.get("damage_taken", 0)
        if damage_val > 0:
            # Функція take_damage сама враховує броню
            msg = db.take_damage(uid, damage_val)
            # Форматуємо повідомлення про урон
            short_msg = msg.split('.')[0] if '.' in msg else msg
            system_msg += f"\n{msg}\n" # Додаємо повне повідомлення
            
            # Перевірка на смерть
            if "ЗАГИНУЛИ" in msg:
                await state.clear() # Вихід з режиму історії
                await message.answer(f"{data.get('text', '...')}\n\n{msg}\n/restart")
                return

        # Д. Лут (Тільки якщо перемога/успіх)
        loot_diff = data.get("loot_difficulty", 0)
        if loot_diff > 0:
            item = db.get_random_loot_by_difficulty(loot_diff)
            if item:
                db.give_item_to_user(uid, item['id'])
                system_msg += f"\n🎁 **Трофей:** Ви знайшли **{item['name']}**!"
            else:
                # Якщо база предметів порожня або не пощастило
                pass

        # Е. Квести (Нові та Завершені)
        if data.get("new_quest"):
            q = data["new_quest"]
            # Додаємо квест. Сюжетні даємо одразу, побічні теж (спрощена логіка)
            db.add_quest(uid, q['name'], q['type'], q['xp'])
            system_msg += f"\n🆕 **Новий Квест:** {q['name']} ({q['type']})"

        if data.get("completed_quest_name"):
            q_name = data["completed_quest_name"]
            xp_reward = db.complete_quest(uid, q_name)
            if xp_reward:
                xp_msg = db.add_xp(uid, xp_reward)
                system_msg += f"\n✅ **Виконано:** {q_name}\n{xp_msg}"

        # Є. Супутники (Додавання в групу)
        if data.get("add_companion"):
            c = data["add_companion"]
            db.add_companion(uid, c['name'], c['race'], c['personality'])
            system_msg += f"\n🤝 **{c['name']}** приєднався до групи!"

        # Ж. Завершення Глави (Перехід)
        if data.get("chapter_complete"):
            next_chap = chapter_data['next_chapter_id']
            if next_chap:
                db.update_user_chapter(uid, next_chap)
                db.clear_ai_history(uid) # Очищаємо контекст для нової глави
                await message.answer("🎉 **ГЛАВА ЗАВЕРШЕНА!**")
                
                # Автоматичний старт наступної глави
                new_chap_data = STORY_CHAPTERS[next_chap]
                await message.answer(f"📖 **{new_chap_data['title']}**")
                
                # Рекурсивний виклик для старту нової глави
                await generate_ai_response(message, state, f"INTRO: Start {new_chap_data['title']}. Describe scene.", uid)
                return
            else:
                await message.answer("🏆 **ВІТАЮ! ГРУ ПРОЙДЕНО!**")
                return

        # --- 7. ВІДПОВІДЬ ГРАВЦЮ ---
        
        story_text = data.get("text", "...")
        
        # Оновлюємо історію діалогу в базі (пам'ять AI)
        db.update_ai_history(uid, f"User: {prompt}\nDM: {story_text}")
        
        # Додаємо системні повідомлення (урон, квести, репутація) до тексту історії
        if system_msg:
            story_text += f"\n\n──────────────\n{system_msg}"
        
        # Формуємо кнопки варіантів
        options = data.get("options", [])
        USER_OPTIONS[uid] = options # Зберігаємо в пам'ять для обробника кнопок
        
        builder = InlineKeyboardBuilder()
        for i, option_text in enumerate(options):
            # Використовуємо індекс для економії місця в callback_data
            builder.button(text=option_text, callback_data=f"aichoice_{i}")
        # Додаємо кнопку для відкриття карти
        builder.button(text="🗺 Карта", callback_data="open_map")
        builder.adjust(1)
        
        # Додаємо настрій NPC, якщо він є
        npc_mood = data.get("npc_mood", "")
        mood_icon = "😐"
        if "Angr" in npc_mood: mood_icon = "😡"
        elif "Happ" in npc_mood or "Grat" in npc_mood: mood_icon = "😊"
        elif "Fear" in npc_mood or "Scar" in npc_mood: mood_icon = "😨"
        
        mood_display = f"\n\n🧠 {npc_mood} {mood_icon}" if npc_mood else ""
        
        # Відправляємо фінальне повідомлення
        await message.answer(f"{story_text}{mood_display}", reply_markup=builder.as_markup())

    except Exception as e:
        print(f"AI Error: {e}")
        await message.answer("⚠️ Магічні перешкоди (AI помилився). Спробуйте ще раз.")

# --- ФУНКЦІЯ СТАРТУ (Викликається з game_handlers.py) ---
async def run_ai_start(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    
    await message.answer("⏳ **Завантаження світу...**")
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    history = db.get_ai_history(uid)
    
    # Якщо історії немає - просимо почати, якщо є - нагадати контекст
    prompt = "SYSTEM: Player returns to game. Remind context." if history else "SYSTEM: Start the chapter. Describe the scene."
    
    await generate_ai_response(message, state, prompt, uid)
    await state.set_state(StoryMode.active)