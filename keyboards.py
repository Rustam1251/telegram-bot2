from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📚 Модули", callback_data="menu_modules"),
        InlineKeyboardButton(text="📊 Мой прогресс", callback_data="menu_progress")
    )
    builder.row(
        InlineKeyboardButton(text="🎯 Рекомендации", callback_data="menu_recommend"),
        InlineKeyboardButton(text="⭐ Избранное", callback_data="menu_favorites")
    )
    builder.row(
        InlineKeyboardButton(text="❓ Спросить Felix", callback_data="menu_ask"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")
    )
    return builder.as_markup()

def modules_keyboard():
    builder = InlineKeyboardBuilder()
    modules = [
        ("🎩 Этикет", "module_etiquette"),
        ("👔 Стиль", "module_style"),
        ("🎨 Искусство", "module_art"),
        ("💰 Финансы", "module_finance"),
        ("✈️ Путешествия", "module_travel"),
        ("⚖️ Право", "module_law"),
        ("🍷 Вино", "module_wine"),
        ("🧠 Психология", "module_psychology"),
        ("🎙️ Ораторство", "module_oratory"),
        ("👑 Лидерство", "module_leadership"),
        ("⏳ Время и досуг", "module_time"),
        ("🌍 Политика", "module_politics")
    ]
    for name, cb in modules:
        builder.row(InlineKeyboardButton(text=name, callback_data=cb))
    builder.row(InlineKeyboardButton(text="🔙 На главную", callback_data="back_main"))
    return builder.as_markup()

def topic_keyboard(module: str):
    """Возвращает клавиатуру с подтемами для выбранного модуля"""
    subtopics_map = {
        "etiquette": [
            ("Основы этикета", "topic_etiquette_basics"),
            ("Столовый этикет", "topic_etiquette_table"),
            ("Светские мероприятия", "topic_etiquette_events"),
            ("Цифровой этикет", "topic_etiquette_digital")
        ],
        "style": [
            ("Базовый гардероб", "topic_style_wardrobe"),
            ("Уход за вещами", "topic_style_care"),
            ("Аксессуары", "topic_style_accessories"),
            ("Дресс-коды", "topic_style_dresscode")
        ],
        "art": [
            ("История искусств", "topic_art_history"),
            ("Музеи мира", "topic_art_museums"),
            ("Классическая музыка", "topic_art_music"),
            ("Архитектура", "topic_art_architecture")
        ],
        "finance": [
            ("Управление бюджетом", "topic_finance_budget"),
            ("Инвестиции", "topic_finance_invest"),
            ("Недвижимость", "topic_finance_realty"),
            ("Благотворительность", "topic_finance_charity")
        ],
        "travel": [
            ("Направления", "topic_travel_destinations"),
            ("Транспорт", "topic_travel_transport"),
            ("Гастрономия", "topic_travel_gastro"),
            ("Этикет путешествий", "topic_travel_etiquette")
        ],
        "law": [
            ("Основы договорного права", "topic_law_contracts"),
            ("Налоговая грамотность", "topic_law_tax"),
            ("Семейное право и наследование", "topic_law_family"),
            ("Защита бизнеса", "topic_law_business"),
            ("Юридическая этика", "topic_law_ethics")
        ],
        "wine": [
            ("Винодельческие регионы", "topic_wine_regions"),
            ("Сорта винограда", "topic_wine_grapes"),
            ("Как читать этикетку", "topic_wine_label"),
            ("Искусство дегустации", "topic_wine_tasting"),
            ("Сочетание с едой", "topic_wine_pairing")
        ],
        "psychology": [
            ("Основы личности", "topic_psychology_personality"),
            ("Эмоциональный интеллект", "topic_psychology_ei"),
            ("Психология влияния", "topic_psychology_influence"),
            ("Защита от манипуляций", "topic_psychology_manipulation"),
            ("Управление стрессом", "topic_psychology_stress")
        ],
        "oratory": [
            ("Техника речи", "topic_oratory_speech"),
            ("Риторика", "topic_oratory_rhetoric"),
            ("Искусство тоста", "topic_oratory_toast"),
            ("Публичные выступления", "topic_oratory_public"),
            ("Речь в digital", "topic_oratory_digital")
        ],
        "leadership": [
            ("Природа лидерства", "topic_leadership_nature"),
            ("Управление командой", "topic_leadership_team"),
            ("Принятие решений", "topic_leadership_decisions"),
            ("Конфликтология", "topic_leadership_conflict"),
            ("Наставничество", "topic_leadership_mentoring")
        ],
        "time": [
            ("Философия времени", "topic_time_philosophy"),
            ("Планирование без стресса", "topic_time_planning"),
            ("Классические хобби", "topic_time_hobbies"),
            ("Путешествия со смыслом", "topic_time_travel"),
            ("Цифровой детокс", "topic_time_detox")
        ],
        "politics": [
            ("Основы политических систем", "topic_politics_systems"),
            ("Политическое устройство стран", "topic_politics_countries"),
            ("Международные отношения", "topic_politics_international"),
            ("Политика и бизнес", "topic_politics_business"),
            ("Политическая философия", "topic_politics_philosophy")
        ]
    }
    subtopics = subtopics_map.get(module, [("В разработке", "topic_dummy")])
    builder = InlineKeyboardBuilder()
    for name, cb in subtopics:
        builder.row(InlineKeyboardButton(text=name, callback_data=cb))
    builder.row(InlineKeyboardButton(text="🔙 К модулям", callback_data="menu_modules"))
    return builder.as_markup()

def lesson_actions_keyboard(lesson_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📝 Тест", callback_data=f"test_{lesson_id}"),
        InlineKeyboardButton(text="📌 В избранное", callback_data=f"save_{lesson_id}")
    )
    builder.row(
        InlineKeyboardButton(text="👍", callback_data=f"like_{lesson_id}"),
        InlineKeyboardButton(text="👎", callback_data=f"dislike_{lesson_id}")
    )
    builder.row(InlineKeyboardButton(text="⏩ Следующий урок", callback_data="next_lesson"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_topic"))
    return builder.as_markup()

def test_keyboard(lesson_id: int, question_idx: int, total: int, options: list):
    builder = InlineKeyboardBuilder()
    for text, cb in options:
        builder.row(InlineKeyboardButton(text=text, callback_data=cb))
    builder.row(InlineKeyboardButton(text="🔙 К уроку", callback_data=f"lesson_{lesson_id}"))
    return builder.as_markup()

def interests_keyboard():
    """Клавиатура для выбора интересов при регистрации"""
    builder = InlineKeyboardBuilder()
    interests = [
        ("🎩 Этикет", "int_etiquette"),
        ("👔 Стиль", "int_style"),
        ("🎨 Искусство", "int_art"),
        ("💰 Финансы", "int_finance"),
        ("✈️ Путешествия", "int_travel"),
        ("⚖️ Право", "int_law"),
        ("🍷 Вино", "int_wine"),
        ("🧠 Психология", "int_psychology"),
        ("🎙️ Ораторство", "int_oratory"),
        ("👑 Лидерство", "int_leadership"),
        ("⏳ Время и досуг", "int_time"),
        ("🌍 Политика", "int_politics")
    ]
    for name, cb in interests:
        builder.row(InlineKeyboardButton(text=name, callback_data=cb))
    builder.row(InlineKeyboardButton(text="✅ Готово", callback_data="int_done"))
    return builder.as_markup()

def level_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1 — Новичок", callback_data="level_1"),
        InlineKeyboardButton(text="2 — Знающий", callback_data="level_2"),
        InlineKeyboardButton(text="3 — Эксперт", callback_data="level_3")
    )
    return builder.as_markup()

def settings_keyboard():
    """Клавиатура для меню настроек"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Изменить уровень", callback_data="settings_level"))
    builder.row(InlineKeyboardButton(text="❤️ Изменить интересы", callback_data="settings_interests"))
    builder.row(InlineKeyboardButton(text="🔙 На главную", callback_data="back_main"))
    return builder.as_markup()

def change_interests_keyboard():
    """Клавиатура для выбора интересов в настройках"""
    builder = InlineKeyboardBuilder()
    interests = [
        ("🎩 Этикет", "int_etiquette"),
        ("👔 Стиль", "int_style"),
        ("🎨 Искусство", "int_art"),
        ("💰 Финансы", "int_finance"),
        ("✈️ Путешествия", "int_travel"),
        ("⚖️ Право", "int_law"),
        ("🍷 Вино", "int_wine"),
        ("🧠 Психология", "int_psychology"),
        ("🎙️ Ораторство", "int_oratory"),
        ("👑 Лидерство", "int_leadership"),
        ("⏳ Время и досуг", "int_time"),
        ("🌍 Политика", "int_politics")
    ]
    for name, cb in interests:
        builder.row(InlineKeyboardButton(text=name, callback_data=cb))
    builder.row(InlineKeyboardButton(text="✅ Готово", callback_data="int_done"))
    return builder.as_markup()
