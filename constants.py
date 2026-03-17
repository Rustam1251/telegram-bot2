# Константы для EGOIST ACADEMY

# Названия модулей
TOPIC_NAMES = {
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

# Названия подтем
SUBTOPIC_NAMES = {
    # Этикет
    "topic_etiquette_basics": "Основы этикета",
    "topic_etiquette_table": "Столовый этикет",
    "topic_etiquette_events": "Светские мероприятия",
    "topic_etiquette_digital": "Цифровой этикет",
    # Стиль
    "topic_style_wardrobe": "Базовый гардероб",
    "topic_style_care": "Уход за вещами",
    "topic_style_accessories": "Аксессуары",
    "topic_style_dresscode": "Дресс-коды",
    # Искусство
    "topic_art_history": "История искусств",
    "topic_art_museums": "Музеи мира",
    "topic_art_music": "Классическая музыка",
    "topic_art_architecture": "Архитектура",
    # Финансы
    "topic_finance_budget": "Управление бюджетом",
    "topic_finance_invest": "Инвестиции",
    "topic_finance_realty": "Недвижимость",
    "topic_finance_charity": "Благотворительность",
    # Путешествия
    "topic_travel_destinations": "Направления",
    "topic_travel_transport": "Транспорт",
    "topic_travel_gastro": "Гастрономия",
    "topic_travel_etiquette": "Этикет путешествий",
    # Право
    "topic_law_contracts": "Основы договорного права",
    "topic_law_tax": "Налоговая грамотность",
    "topic_law_family": "Семейное право и наследование",
    "topic_law_business": "Защита бизнеса",
    "topic_law_ethics": "Юридическая этика",
    # Вино
    "topic_wine_regions": "Винодельческие регионы",
    "topic_wine_grapes": "Сорта винограда",
    "topic_wine_label": "Как читать этикетку",
    "topic_wine_tasting": "Искусство дегустации",
    "topic_wine_pairing": "Сочетание с едой",
    # Психология
    "topic_psychology_personality": "Основы личности",
    "topic_psychology_ei": "Эмоциональный интеллект",
    "topic_psychology_influence": "Психология влияния",
    "topic_psychology_manipulation": "Защита от манипуляций",
    "topic_psychology_stress": "Управление стрессом",
    # Ораторство
    "topic_oratory_speech": "Техника речи",
    "topic_oratory_rhetoric": "Риторика",
    "topic_oratory_toast": "Искусство тоста",
    "topic_oratory_public": "Публичные выступления",
    "topic_oratory_digital": "Речь в digital",
    # Лидерство
    "topic_leadership_nature": "Природа лидерства",
    "topic_leadership_team": "Управление командой",
    "topic_leadership_decisions": "Принятие решений",
    "topic_leadership_conflict": "Конфликтология",
    "topic_leadership_mentoring": "Наставничество",
    # Время и досуг
    "topic_time_philosophy": "Философия времени",
    "topic_time_planning": "Планирование без стресса",
    "topic_time_hobbies": "Классические хобби",
    "topic_time_travel": "Путешествия со смыслом",
    "topic_time_detox": "Цифровой детокс",
    # Политика
    "topic_politics_systems": "Основы политических систем",
    "topic_politics_countries": "Политическое устройство стран",
    "topic_politics_international": "Международные отношения",
    "topic_politics_business": "Политика и бизнес",
    "topic_politics_philosophy": "Политическая философия"
}

# Все темы по модулям
ALL_TOPICS = {
    "etiquette": ["topic_etiquette_basics", "topic_etiquette_table", "topic_etiquette_events", "topic_etiquette_digital"],
    "style": ["topic_style_wardrobe", "topic_style_care", "topic_style_accessories", "topic_style_dresscode"],
    "art": ["topic_art_history", "topic_art_museums", "topic_art_music", "topic_art_architecture"],
    "finance": ["topic_finance_budget", "topic_finance_invest", "topic_finance_realty", "topic_finance_charity"],
    "travel": ["topic_travel_destinations", "topic_travel_transport", "topic_travel_gastro", "topic_travel_etiquette"],
    "law": ["topic_law_contracts", "topic_law_tax", "topic_law_family", "topic_law_business", "topic_law_ethics"],
    "wine": ["topic_wine_regions", "topic_wine_grapes", "topic_wine_label", "topic_wine_tasting", "topic_wine_pairing"],
    "psychology": ["topic_psychology_personality", "topic_psychology_ei", "topic_psychology_influence", "topic_psychology_manipulation", "topic_psychology_stress"],
    "oratory": ["topic_oratory_speech", "topic_oratory_rhetoric", "topic_oratory_toast", "topic_oratory_public", "topic_oratory_digital"],
    "leadership": ["topic_leadership_nature", "topic_leadership_team", "topic_leadership_decisions", "topic_leadership_conflict", "topic_leadership_mentoring"],
    "time": ["topic_time_philosophy", "topic_time_planning", "topic_time_hobbies", "topic_time_travel", "topic_time_detox"],
    "politics": ["topic_politics_systems", "topic_politics_countries", "topic_politics_international", "topic_politics_business", "topic_politics_philosophy"]
}

# Лимиты и настройки
EXP_PER_LESSON = 10
EXP_PER_LEVEL = 100
MAX_LEVEL = 10
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_PERIOD = 60
