import json
import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import Registration, Settings, LessonFlow
from keyboards import *
from database import *
from utils import generate_lesson, ask_felix, TOPIC_NAMES, TOPIC_TO_MODULE

router = Router()

# ---------- Проверка подписки ----------
@router.callback_query(F.data == "check_subscription")
async def handle_check_subscription(callback: CallbackQuery):
    # Middleware уже обработал проверку и пропустил сюда — значит подписка есть
    user = await get_user(callback.from_user.id)
    if user:
        await callback.message.edit_text(
            f"🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
            f"Рад приветствовать Вас, *{user['first_name']}*.\n\n"
            f"Я — Felix, Ваш личный консьерж.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
            "Подписка подтверждена! Введите /start для регистрации.",
            parse_mode="Markdown"
        )
    await callback.answer("✅ Добро пожаловать!")

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        # Персонализированное приветствие в зависимости от уровня
        if user['level'] <= 3:
            greeting = (
                f"🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
                f"Рад приветствовать Вас вновь, *{user['first_name']}*.\n\n"
                f"Я — Felix, Ваш личный консьерж.\n"
                f"Чем могу быть полезен сегодня?"
            )
        elif user['level'] <= 6:
            greeting = (
                f"🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
                f"Какая радость видеть Вас снова, *{user['first_name']}*.\n\n"
                f"Позвольте продолжить наше путешествие в мир утончённости."
            )
        else:
            greeting = (
                f"🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
                f"Честь видеть Вас, *{user['first_name']}*.\n\n"
                f"Ваше стремление к совершенству вдохновляет.\n"
                f"Чем могу быть полезен сегодня?"
            )
        
        await message.answer(greeting, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        await state.set_state(Registration.waiting_for_name)
        await message.answer(
            "🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
            "Я — Felix, Ваш личный консьерж в мире утончённости и элегантности.\n\n"
            "Здесь мы культивируем искусство жить с достоинством, вкусом и изяществом.\n\n"
            "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            "Позвольте узнать, как мне к Вам обращаться?",
            parse_mode="Markdown"
        )

@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or any(ch.isdigit() for ch in name):
        await message.answer(
            "Прошу прощения, но позвольте уточнить — как именно мне следует к Вам обращаться?\n\n"
            "Пожалуйста, укажите Ваше имя."
        )
        return
    await state.update_data(first_name=name)
    await state.set_state(Registration.waiting_for_interests)
    await message.answer(
        f"✨ Очень приятно познакомиться, *{name}*.\n\n"
        f"В нашей академии мы предлагаем пять направлений совершенствования.\n\n"
        f"Какие из них вызывают у Вас наибольший интерес?\n"
        f"_Вы можете выбрать несколько._",
        parse_mode="Markdown",
        reply_markup=interests_keyboard()
    )

@router.callback_query(Registration.waiting_for_interests, F.data.startswith("int_"))
async def process_interest(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    interests = data.get("interests", [])
    choice = callback.data.replace("int_", "")
    if choice == "done":
        if not interests:
            await callback.answer("Позвольте узнать хотя бы одно направление, которое Вас интересует.", show_alert=True)
            return
        await state.update_data(interests=",".join(interests))
        await state.set_state(Registration.waiting_for_level)
        await callback.message.edit_text(
            "✨ Превосходно.\n\n"
            "Теперь позвольте определить отправную точку нашего путешествия.\n\n"
            "Как бы Вы оценили свой текущий уровень знаний в выбранных областях?",
            parse_mode="Markdown",
            reply_markup=level_keyboard()
        )
    else:
        if choice not in interests:
            interests.append(choice)
            await state.update_data(interests=interests)
        interest_names = {
            "etiquette": "Этикет",
            "style": "Стиль",
            "art": "Искусство",
            "finance": "Финансы",
            "travel": "Путешествия"
        }
        await callback.answer(f"✓ {interest_names.get(choice, choice)}")

@router.callback_query(Registration.waiting_for_level, F.data.startswith("level_"))
async def process_level(callback: CallbackQuery, state: FSMContext):
    level = int(callback.data.split("_")[1])
    data = await state.get_data()
    first_name = data["first_name"]
    interests = data["interests"] if isinstance(data["interests"], str) else ",".join(data["interests"])
    await add_user(callback.from_user.id, first_name, interests, level)
    await state.clear()
    
    # Персонализированное завершение регистрации
    if level == 1:
        final_msg = (
            f"Прекрасно, *{first_name}*.\n\n"
            f"Ваша готовность учиться — первый шаг к истинной элегантности.\n\n"
            f"Я буду сопровождать Вас на этом пути, деликатно направляя к вершинам утончённости."
        )
    elif level == 2:
        final_msg = (
            f"Замечательно, *{first_name}*.\n\n"
            f"Вы уже обладаете базовыми знаниями — теперь мы отточим их до совершенства.\n\n"
            f"Позвольте мне стать Вашим проводником в мир истинного изящества."
        )
    else:
        final_msg = (
            f"Впечатляюще, *{first_name}*.\n\n"
            f"Ваша эрудиция делает Вам честь.\n\n"
            f"Буду рад поделиться с Вами тонкостями и нюансами, которые отличают истинного ценителя."
        )
    
    await callback.message.edit_text(
        f"🎩 {final_msg}\n\n"
        f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
        f"*Добро пожаловать в EGOIST ACADEMY*",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# ---------- Главное меню ----------
@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"🎩 *Главное меню*\n\n"
        f"Чем могу быть полезен, *{user['first_name']}*?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

# ---------- Модули ----------
@router.callback_query(F.data == "menu_modules")
async def show_modules(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 *Образовательные модули*\n\n"
        "Выберите направление для изучения:",
        parse_mode="Markdown",
        reply_markup=modules_keyboard()
    )

@router.callback_query(F.data.startswith("module_"))
async def show_topics(callback: CallbackQuery):
    from quotes import MODULE_QUOTES, MODULE_DESCRIPTIONS
    
    module = callback.data.replace("module_", "")
    
    quote = MODULE_QUOTES.get(module, "")
    description = MODULE_DESCRIPTIONS.get(module, "Модуль в разработке.")
    
    welcome_text = f"{quote}\n\n{description}"
    
    # Отправляем приветствие модуля с цитатой
    await callback.message.answer(
        welcome_text,
        parse_mode="Markdown"
    )
    
    # Затем отправляем список тем
    await callback.message.answer(
        "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
        "*Выберите тему для изучения:*",
        parse_mode="Markdown",
        reply_markup=topic_keyboard(module)
    )
    await callback.answer()

# ---------- Запрос урока ----------
@router.callback_query(F.data.startswith("topic_"))
async def request_lesson(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    
    if not user:
        await callback.message.answer("Ошибка: пользователь не найден.")
        await log_user_action(callback.from_user.id, "lesson_request_error", "User not found")
        return
    
    await callback.message.edit_text(
        f"⏳ *Минуту терпения, {user['first_name']}...*\n\n"
        f"Я подбираю для Вас материал, который будет соответствовать Вашему уровню и интересам.\n\n"
        f"_Это займёт 10-15 секунд..._",
        parse_mode="Markdown"
    )
    
    # Получаем topic и subtopic из callback_data
    topic_callback = callback.data
    
    # Используем словари из utils
    subtopic = TOPIC_NAMES.get(topic_callback, topic_callback.replace("topic_", "").replace("_", " ").capitalize())
    module = TOPIC_TO_MODULE.get(topic_callback, "etiquette")
    
    # Определяем название модуля
    module_names = {
        "etiquette": "Этикет",
        "style": "Стиль",
        "art": "Искусство",
        "finance": "Финансы",
        "travel": "Путешествия",
        "law": "Право",
        "wine": "Вино",
        "psychology": "Психология",
        "oratory": "Ораторство",
        "leadership": "Лидерство",
        "time": "Время и досуг",
        "politics": "Политика"
    }
    topic = module_names.get(module, module.capitalize())
    
    # Сохраняем информацию о текущей подтеме в state
    await state.set_state(LessonFlow.viewing_lesson)
    await state.update_data(
        current_topic=topic,
        current_subtopic=subtopic,
        current_module=module,
        current_topic_callback=topic_callback
    )
    
    # Генерация урока с обработкой ошибок и таймаутом
    try:
        import asyncio
        lesson_data = await asyncio.wait_for(
            generate_lesson(user["first_name"], user["level"], topic, subtopic),
            timeout=45.0
        )
        lesson_id = await save_lesson(user["id"], topic, subtopic, lesson_data["content"], lesson_data["questions"])
        await add_progress(user["id"], lesson_id)
        
        # Логируем успешное создание урока
        await log_user_action(user["id"], "lesson_generated", f"{topic}: {subtopic}")
        
        # Отправка с подписью Felix
        text = (
            f"✨ *{subtopic}*\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"{lesson_data['content']}\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"_— С надеждой на новые открытия,_\n"
            f"*Felix* 🎩"
        )
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=lesson_actions_keyboard(lesson_id)
        )
    except asyncio.TimeoutError:
        logging.error(f"Timeout generating lesson for user {user['id']}")
        await log_user_action(user["id"], "lesson_timeout", f"{topic}: {subtopic}")
        await callback.message.answer(
            "😔 *Прошу прощения*\n\n"
            "Генерация урока заняла слишком много времени.\n\n"
            "Пожалуйста, попробуйте ещё раз или выберите другую тему.\n\n"
            "_Возможно, сервис AI временно перегружен._",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logging.error(f"Lesson generation failed for user {user['id']}: {e}")
        await log_user_action(user["id"], "lesson_generation_error", str(e))
        await callback.message.answer(
            "😔 *Прошу прощения*\n\n"
            "Произошла техническая ошибка при подготовке урока.\n\n"
            "Пожалуйста, попробуйте позже или выберите другую тему.\n\n"
            "_Приношу извинения за неудобства._",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

# ---------- Тестирование ----------
@router.callback_query(F.data.startswith("test_"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split("_")[1])
    lesson = await get_lesson(lesson_id)
    if not lesson:
        await callback.answer("Урок не найден")
        return
    questions = json.loads(lesson[5])
    if not questions:
        await callback.answer("Нет вопросов для этого урока.")
        return
    await state.update_data(lesson_id=lesson_id, questions=questions, current_q=0, score=0)
    await send_question(callback.message, state)

async def send_question(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_q"]
    q = questions[idx]
    options = []
    for opt in q["options"]:
        letter = opt[0]
        options.append((opt, f"ans_{idx}_{letter}"))
    kb = test_keyboard(data["lesson_id"], idx, len(questions), options)
    await message.answer(
        f"❓ *Вопрос {idx+1} из {len(questions)}*\n\n"
        f"{q['question']}\n\n"
        f"_Выберите вариант ответа:_",
        parse_mode="Markdown",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("ans_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    q_idx = int(parts[1])
    answer_letter = parts[2]
    data = await state.get_data()
    questions = data["questions"]
    if q_idx != data["current_q"]:
        await callback.answer("Устаревший запрос")
        return
    correct = questions[q_idx]["correct"]
    is_correct = (answer_letter == correct)
    new_score = data["score"] + (1 if is_correct else 0)
    await state.update_data(score=new_score)
    
    if is_correct:
        await callback.answer("✅ Верно!", show_alert=False)
    else:
        await callback.answer(f"❌ Неверно. Правильный ответ: {correct}", show_alert=True)
    
    if q_idx + 1 < len(questions):
        await state.update_data(current_q=q_idx + 1)
        await send_question(callback.message, state)
    else:
        user = await get_user(callback.from_user.id)
        await update_progress_score(user["id"], data["lesson_id"], new_score)
        
        # Персонализированное завершение теста
        if new_score == len(questions):
            result_msg = "🏆 *Превосходно!*\n\nВы ответили на все вопросы правильно."
        elif new_score >= len(questions) * 0.7:
            result_msg = "✨ *Отличный результат!*\n\nВы продемонстрировали хорошее понимание материала."
        else:
            result_msg = "📚 *Хороший старт!*\n\nРекомендую ещё раз просмотреть материал урока."
        
        await callback.message.answer(
            f"{result_msg}\n\n"
            f"Ваш результат: *{new_score}/{len(questions)}*\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"_Продолжайте совершенствоваться!_\n"
            f"*Felix* 🎩",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()

# ---------- Обратная связь (лайк/дизлайк) ----------
@router.callback_query(F.data.startswith("like_"))
async def like_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    user = await get_user(callback.from_user.id)
    await update_progress_like(user["id"], lesson_id, True)
    await callback.answer("✨ Благодарю за оценку! Ваше мнение помогает нам совершенствоваться.", show_alert=False)

@router.callback_query(F.data.startswith("dislike_"))
async def dislike_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    user = await get_user(callback.from_user.id)
    await update_progress_like(user["id"], lesson_id, False)
    await callback.answer("Благодарю за честность. Мы учтём Ваш отзыв для улучшения качества.", show_alert=False)

# ---------- Прогресс ----------
@router.callback_query(F.data == "menu_progress")
async def show_progress(callback: CallbackQuery):
    prog = await get_user_progress(callback.from_user.id)
    if prog:
        # Вычисляем прогресс-бар
        level = prog['level']
        total_lessons = prog['total_lessons']
        
        # Опыт = количество пройденных уроков * 10
        experience = total_lessons * 10
        next_level_exp = (level + 1) * 100
        
        # Опыт на текущем уровне
        exp_current_level = experience - (level * 100)
        if exp_current_level < 0:
            exp_current_level = experience
        
        progress_percent = min(100, int(exp_current_level / 100 * 100))
        bar_length = 20
        filled = int(bar_length * progress_percent / 100)
        progress_bar = "█" * filled + "░" * (bar_length - filled)
        
        text = (
            f"📊 *ВАШ ПРОГРЕСС*\n\n"
            f"┌─────────────────────────────────\n"
            f"│ 🎓 Уровень: *{prog['level']}*\n"
            f"│ 📚 Пройдено уроков: *{prog['total_lessons']}*\n"
            f"│ 📈 Средний балл: *{prog['avg_score']}*\n"
            f"│ ✨ Опыт: *{experience}* / {next_level_exp}\n"
            f"│ [{progress_bar}] {progress_percent}%\n"
            f"└─────────────────────────────────\n\n"
            f"_Продолжайте в том же духе!_"
        )
    else:
        text = (
            f"📊 *ВАШ ПРОГРЕСС*\n\n"
            f"У вас пока нет пройденных уроков.\n\n"
            f"_Начните своё путешествие в мир утончённости!_"
        )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

# ---------- Рекомендации ----------
@router.callback_query(F.data == "menu_recommend")
async def recommend(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    
    if not user:
        await callback.answer("Ошибка: пользователь не найден")
        return
    
    # Получаем умную рекомендацию
    recommendation = await get_smart_recommendation(user["id"])
    
    if not recommendation:
        await callback.message.edit_text(
            f"🎯 *Рекомендация для Вас, {user['first_name']}*\n\n"
            f"Вы прошли все доступные темы! Поздравляю с таким достижением.\n\n"
            f"_Скоро появятся новые модули._",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return
    
    if recommendation["type"] == "weak":
        # Рекомендуем повторить слабую тему
        message = (
            f"🎯 *Рекомендация для Вас, {user['first_name']}*\n\n"
            f"Я заметил, что тема «{recommendation['subtopic']}» из модуля «{recommendation['topic']}» "
            f"может потребовать дополнительного внимания.\n\n"
            f"{recommendation['reason']}\n\n"
            f"_Повторение — мать учения._\n\n"
            f"Желаете вернуться к этой теме?"
        )
        # Для слабых тем нужно найти callback_data
        callback_data = "topic_etiquette_basics"  # По умолчанию
    else:
        # Рекомендуем новую тему
        message = (
            f"🎯 *Рекомендация для Вас, {user['first_name']}*\n\n"
            f"Основываясь на Ваших интересах, советую изучить тему «{recommendation['subtopic']}» "
            f"из модуля «{recommendation['topic']}».\n\n"
            f"_{recommendation['reason']}_\n\n"
            f"Желаете перейти?"
        )
        callback_data = f"topic_{recommendation['module']}_{recommendation['subtopic_key']}"
    
    await callback.message.edit_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✨ Перейти к уроку", callback_data=callback_data)],
            [InlineKeyboardButton(text="🔙 На главную", callback_data="back_main")]
        ])
    )

# ---------- Задать вопрос ----------
@router.callback_query(F.data == "menu_ask")
async def ask_question(callback: CallbackQuery, state: FSMContext):
    await state.set_state("waiting_question")
    await callback.message.edit_text(
        "💬 *Я весь внимание*\n\n"
        "Задайте Ваш вопрос, и я постараюсь дать исчерпывающий ответ, "
        "основанный на принципах утончённости и хорошего вкуса.\n\n"
        "_Напишите Ваш вопрос текстом..._",
        parse_mode="Markdown"
    )

@router.message(StateFilter("waiting_question"))
async def handle_question(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    
    if not user:
        await message.answer("Ошибка: пользователь не найден.")
        await state.clear()
        return
    
    try:
        # Логируем вопрос пользователя
        await log_user_action(user["id"], "question_asked", message.text[:100])
        
        answer = await asyncio.wait_for(
            ask_felix(message.text, user["first_name"]),
            timeout=30.0
        )
        
        await message.answer(
            f"🕊️ *Ответ от Felix*\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"{answer}\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"_Всегда к Вашим услугам,_\n"
            f"*Felix* 🎩",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    except asyncio.TimeoutError:
        logging.error(f"Timeout answering question for user {user['id']}")
        await log_user_action(user["id"], "question_timeout", message.text[:100])
        await message.answer(
            "😔 *Прошу прощения*\n\n"
            "Ответ на Ваш вопрос занял слишком много времени.\n\n"
            "Пожалуйста, попробуйте переформулировать вопрос или задайте его позже.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logging.error(f"Question handling failed for user {user['id']}: {e}")
        await log_user_action(user["id"], "question_error", str(e))
        await message.answer(
            "😔 *Прошу прощения*\n\n"
            "Произошла техническая ошибка при обработке Вашего вопроса.\n\n"
            "Пожалуйста, попробуйте позже.\n\n"
            "_Приношу извинения за неудобства._",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    finally:
        await state.clear()

# ---------- Настройки ----------
@router.callback_query(F.data == "menu_settings")
async def settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ *Настройки*\n\n"
        "Выберите что хотите изменить:",
        parse_mode="Markdown",
        reply_markup=settings_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "settings_level")
async def settings_change_level(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Settings.changing_level)
    await callback.message.edit_text(
        "📊 *Выберите новый уровень*\n\n"
        "1 — Новичок (начинаю с нуля)\n"
        "2 — Знающий (знаю основы)\n"
        "3 — Эксперт (углубленное изучение)",
        parse_mode="Markdown",
        reply_markup=level_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("level_"), Settings.changing_level)
async def process_settings_level(callback: CallbackQuery, state: FSMContext):
    level = int(callback.data.split("_")[1])
    
    await update_user_level_by_telegram_id(callback.from_user.id, level)
    await state.clear()
    
    level_labels = {1: "Новичок", 2: "Знающий", 3: "Эксперт"}
    await callback.message.edit_text(
        f"✅ *Уровень изменён*\n\n"
        f"Ваш новый уровень: *{level} — {level_labels.get(level, str(level))}*",
        parse_mode="Markdown",
        reply_markup=settings_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "settings_interests")
async def settings_change_interests(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Settings.changing_interests)
    await callback.message.edit_text(
        "❤️ *Выберите интересы*\n\n"
        "_Можно выбрать несколько_",
        parse_mode="Markdown",
        reply_markup=change_interests_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("int_"), Settings.changing_interests)
async def process_settings_interests(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    interests = data.get("interests", [])
    choice = callback.data.replace("int_", "")
    
    interest_names = {
        "etiquette": "Этикет",
        "style": "Стиль",
        "art": "Искусство",
        "finance": "Финансы",
        "travel": "Путешествия",
        "law": "Право",
        "wine": "Вино",
        "psychology": "Психология",
        "oratory": "Ораторство",
        "leadership": "Лидерство",
        "time": "Время и досуг",
        "politics": "Политика"
    }
    
    if choice == "done":
        if not interests:
            await callback.answer("Выберите хотя бы один интерес.", show_alert=True)
            return
        
        interests_str = ",".join(interests)
        await update_user_interests(callback.from_user.id, interests_str)
        
        await state.clear()
        await callback.message.edit_text(
            f"✅ *Интересы обновлены*\n\n"
            f"Выбрано: {', '.join([interest_names.get(i, i) for i in interests])}",
            parse_mode="Markdown",
            reply_markup=settings_keyboard()
        )
        await callback.answer()
    else:
        if choice not in interests:
            interests.append(choice)
            await state.update_data(interests=interests)
            await callback.answer(f"✓ {interest_names.get(choice, choice)}")
        else:
            interests.remove(choice)
            await state.update_data(interests=interests)
            await callback.answer(f"✗ {interest_names.get(choice, choice)}")

# ---------- Вспомогательные навигационные кнопки ----------
@router.callback_query(F.data == "back_to_topic")
async def back_to_topic(callback: CallbackQuery):
    await show_modules(callback)

@router.callback_query(F.data == "next_lesson")
async def next_lesson(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    
    if not user:
        await callback.answer("Ошибка: пользователь не найден.", show_alert=True)
        return
    
    # Получаем сохранённые данные о текущей подтеме
    data = await state.get_data()
    current_topic = data.get("current_topic")
    current_subtopic = data.get("current_subtopic")
    current_module = data.get("current_module")
    
    if not current_topic or not current_subtopic:
        await callback.answer("Ошибка: информация о теме потеряна. Выберите тему заново.", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"⏳ *Подготавливаю новый урок...*\n\n"
        f"_Это займёт 10-15 секунд..._",
        parse_mode="Markdown"
    )
    
    try:
        import asyncio
        lesson_data = await asyncio.wait_for(
            generate_lesson(user["first_name"], user["level"], current_topic, current_subtopic),
            timeout=45.0
        )
        lesson_id = await save_lesson(user["id"], current_topic, current_subtopic, lesson_data["content"], lesson_data["questions"])
        await add_progress(user["id"], lesson_id)
        
        await log_user_action(user["id"], "next_lesson_generated", f"{current_topic}: {current_subtopic}")
        
        text = (
            f"✨ *{current_subtopic}*\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"{lesson_data['content']}\n\n"
            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
            f"_— С надеждой на новые открытия,_\n"
            f"*Felix* 🎩"
        )
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=lesson_actions_keyboard(lesson_id)
        )
    except asyncio.TimeoutError:
        logging.error(f"Timeout generating next lesson for user {user['id']}")
        await callback.message.answer(
            "😔 *Прошу прощения*\n\n"
            "Генерация урока заняла слишком много времени.\n\n"
            "Пожалуйста, попробуйте ещё раз.",
            parse_mode="Markdown",
            reply_markup=lesson_actions_keyboard(0)
        )
    except Exception as e:
        logging.error(f"Next lesson generation failed for user {user['id']}: {e}")
        await callback.message.answer(
            "😔 *Прошу прощения*\n\n"
            "Произошла техническая ошибка при подготовке урока.",
            parse_mode="Markdown",
            reply_markup=lesson_actions_keyboard(0)
        )

@router.callback_query(F.data.startswith("save_"))
async def save_lesson_favorite(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден")
        return
    
    success = await add_favorite(user["id"], lesson_id)
    if success:
        await log_user_action(user["id"], "favorite_added", f"lesson_id: {lesson_id}")
        await callback.answer("📌 Урок добавлен в избранное!", show_alert=False)
    else:
        await callback.answer("Урок уже в избранном", show_alert=False)

# ---------- Просмотр избранного ----------
@router.callback_query(F.data == "menu_favorites")
async def show_favorites_menu(callback: CallbackQuery, page: int = 0):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка")
        return
    
    favorites = await get_favorites(user["id"])
    
    if not favorites:
        await callback.message.edit_text(
            "⭐ *Ваше избранное*\n\n"
            "У вас пока нет сохранённых уроков.\n\n"
            "_Добавляйте понравившиеся уроки, чтобы вернуться к ним позже._",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Пагинация: 5 уроков на страницу
    items_per_page = 5
    total_pages = (len(favorites) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(favorites))
    page_favorites = favorites[start_idx:end_idx]
    
    # Формируем список с кнопками для каждого урока
    builder = InlineKeyboardBuilder()
    for lesson in page_favorites:
        builder.row(InlineKeyboardButton(
            text=f"📖 {lesson['topic']}: {lesson['subtopic']}",
            callback_data=f"fav_lesson_{lesson['id']}"
        ))
    
    # Кнопки навигации по страницам
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"fav_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"fav_page_{page+1}"))
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton(text="🔙 На главную", callback_data="back_main"))
    
    await callback.message.edit_text(
        f"⭐ *Ваше избранное*\n\n"
        f"Сохранено уроков: *{len(favorites)}*\n"
        f"Страница {page+1} из {total_pages}\n\n"
        f"_Выберите урок для просмотра:_",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("fav_page_"))
async def favorites_pagination(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await show_favorites_menu(callback, page)

@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    await callback.answer()

@router.callback_query(F.data.startswith("fav_lesson_"))
async def show_favorite_lesson(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[2])
    lesson = await get_lesson(lesson_id)
    
    if not lesson:
        await callback.answer("Урок не найден")
        return
    
    # lesson это кортеж: (id, user_id, topic, subtopic, content, questions, rating, created_at)
    text = (
        f"✨ *{lesson[3]}*\n\n"  # subtopic
        f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
        f"{lesson[4]}\n\n"  # content
        f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n\n"
        f"_— Из вашего избранного,_\n"
        f"*Felix* 🎩"
    )
    
    # Кнопки для действий с уроком
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Пройти тест", callback_data=f"test_{lesson_id}"),
        InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"unfav_{lesson_id}")
    )
    builder.row(InlineKeyboardButton(text="🔙 К избранному", callback_data="menu_favorites"))
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("unfav_"))
async def remove_from_favorites(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    user = await get_user(callback.from_user.id)
    await remove_favorite(user["id"], lesson_id)
    await log_user_action(user["id"], "favorite_removed", f"lesson_id: {lesson_id}")
    await callback.answer("Урок удалён из избранного")
    # Возвращаемся к списку избранного
    await show_favorites_menu(callback)
