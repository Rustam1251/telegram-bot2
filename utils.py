import openai
import json
import re
import logging
import aiosqlite
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, LOG_FILE, DATABASE_PATH

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаём клиент OpenAI с настройками для Groq
client = openai.AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL
)

# Словарь для преобразования callback_data в человекочитаемые названия тем
TOPIC_NAMES = {
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

# Словарь для определения модуля по теме
TOPIC_TO_MODULE = {
    # Этикет
    "topic_etiquette_basics": "etiquette",
    "topic_etiquette_table": "etiquette",
    "topic_etiquette_events": "etiquette",
    "topic_etiquette_digital": "etiquette",
    # Стиль
    "topic_style_wardrobe": "style",
    "topic_style_care": "style",
    "topic_style_accessories": "style",
    "topic_style_dresscode": "style",
    # Искусство
    "topic_art_history": "art",
    "topic_art_museums": "art",
    "topic_art_music": "art",
    "topic_art_architecture": "art",
    # Финансы
    "topic_finance_budget": "finance",
    "topic_finance_invest": "finance",
    "topic_finance_realty": "finance",
    "topic_finance_charity": "finance",
    # Путешествия
    "topic_travel_destinations": "travel",
    "topic_travel_transport": "travel",
    "topic_travel_gastro": "travel",
    "topic_travel_etiquette": "travel",
    # Право
    "topic_law_contracts": "law",
    "topic_law_tax": "law",
    "topic_law_family": "law",
    "topic_law_business": "law",
    "topic_law_ethics": "law",
    # Вино
    "topic_wine_regions": "wine",
    "topic_wine_grapes": "wine",
    "topic_wine_label": "wine",
    "topic_wine_tasting": "wine",
    "topic_wine_pairing": "wine",
    # Психология
    "topic_psychology_personality": "psychology",
    "topic_psychology_ei": "psychology",
    "topic_psychology_influence": "psychology",
    "topic_psychology_manipulation": "psychology",
    "topic_psychology_stress": "psychology",
    # Ораторство
    "topic_oratory_speech": "oratory",
    "topic_oratory_rhetoric": "oratory",
    "topic_oratory_toast": "oratory",
    "topic_oratory_public": "oratory",
    "topic_oratory_digital": "oratory",
    # Лидерство
    "topic_leadership_nature": "leadership",
    "topic_leadership_team": "leadership",
    "topic_leadership_decisions": "leadership",
    "topic_leadership_conflict": "leadership",
    "topic_leadership_mentoring": "leadership",
    # Время и досуг
    "topic_time_philosophy": "time",
    "topic_time_planning": "time",
    "topic_time_hobbies": "time",
    "topic_time_travel": "time",
    "topic_time_detox": "time",
    # Политика
    "topic_politics_systems": "politics",
    "topic_politics_countries": "politics",
    "topic_politics_international": "politics",
    "topic_politics_business": "politics",
    "topic_politics_philosophy": "politics"
}

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError))
)
async def generate_lesson(user_name: str, level: int, topic: str, subtopic: str) -> dict:
    """
    Генерирует урок с помощью Groq с автоматическими повторами при ошибках.
    Возвращает словарь: {'content': str, 'questions': json str}
    """
    try:
        # Определяем стиль обращения в зависимости от уровня
        if level <= 3:
            level_desc = "начинающий, требует деликатного введения в тему"
            tone = "доступным, но изысканным языком"
        elif level <= 6:
            level_desc = "знающий основы, готов к более глубоким знаниям"
            tone = "утончённым языком с отсылками к классике"
        else:
            level_desc = "эксперт, ценит тонкости и нюансы"
            tone = "языком истинного ценителя, с изысканными деталями"
        
        prompt = f"""Ты — Felix, личный консьерж академии EGOIST ACADEMY в традициях old money.

Твоя задача — создать персонализированный урок для {user_name} (уровень {level}/10 — {level_desc}) по теме "{subtopic}" в рамках модуля "{topic}".

СТИЛЬ ОБЩЕНИЯ:
- Обращайся к {user_name} с почтительным уважением, используя "Вы"
- Пиши {tone}
- Используй метафоры из мира классического искусства, архитектуры, высокой культуры
- Избегай банальностей — каждая фраза должна нести ценность
- Демонстрируй эрудицию, но без высокомерия
- Приводи примеры из жизни аристократии, известных династий, классических произведений

СТРУКТУРА УРОКА:
1. Элегантное вступление (2-3 предложения) — установи контакт с {user_name}
2. Историческая справка (2-3 предложения) — откуда пришла традиция/знание
3. Практический пример из жизни (конкретная ситуация)
4. Совет от Felix (как применить в современной жизни)
5. Рекомендация книги или фильма по теме
6. Изящное заключение (1-2 предложения) — подведи итог

Длина урока: 800-1000 знаков.

После урока добавь строку "ВОПРОСЫ:" и три вопроса для самопроверки:

1. Текст вопроса?
A) вариант 1
B) вариант 2
C) вариант 3
Правильный ответ: A

Вопросы должны проверять понимание, а не просто память. Формулируй их изящно."""
        
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
            timeout=30.0
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Пустой ответ от API")
        
        full_content = response.choices[0].message.content
        
        # Разделяем текст и вопросы
        if "ВОПРОСЫ:" in full_content:
            parts = full_content.split("ВОПРОСЫ:")
            lesson_text = parts[0].strip()
            questions_part = parts[1].strip()
        else:
            lesson_text = full_content.strip()
            questions_part = ""
        
        # Парсим вопросы
        questions = []
        if questions_part:
            lines = questions_part.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if re.match(r'^\d+\.', line):
                    q_text = line
                    i += 1
                    options = []
                    while i < len(lines) and re.match(r'^[A-C]\)', lines[i].strip()):
                        options.append(lines[i].strip())
                        i += 1
                    correct = ""
                    if i < len(lines) and "Правильный ответ:" in lines[i]:
                        correct = lines[i].split(":")[-1].strip()
                        i += 1
                    questions.append({
                        "question": q_text,
                        "options": options,
                        "correct": correct
                    })
                else:
                    i += 1
        
        return {
            "content": lesson_text,
            "questions": json.dumps(questions, ensure_ascii=False)
        }
    except Exception as e:
        logger.error(f"Error generating lesson for {user_name}: {e}")
        raise

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError))
)
async def ask_felix(question: str, user_name: str) -> str:
    """Ответ на свободный вопрос пользователя с автоматическими повторами"""
    try:
        prompt = f"""Ты — Felix, личный консьерж академии EGOIST ACADEMY в традициях old money.

{user_name} обращается к тебе с вопросом. Твоя задача — дать изысканный, содержательный ответ.

СТИЛЬ ОТВЕТА:
- Обращайся к {user_name} с уважением на "Вы"
- Начни с элегантного приветствия или признания вопроса
- Отвечай обстоятельно, но лаконично (250-350 знаков)
- Используй типографские кавычки («»), избегай сленга
- Используй примеры из классической культуры, истории, искусства
- Завершай ответ изящной фразой или советом
- Демонстрируй эрудицию и вкус, но оставайся доступным

Если вопрос не по теме (этикет, стиль, искусство, финансы, путешествия), вежливо укажи на это.

Вопрос {user_name}: {question}

Твой ответ:"""
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5,
            max_tokens=400,
            timeout=20.0
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Пустой ответ от API")
        
        answer = response.choices[0].message.content
        
        # Сохраняем вопрос и ответ в базу знаний
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO knowledge_base (query, answer, source) VALUES (?, ?, ?)",
                (question, answer, "groq")
            )
            await db.commit()
        
        return answer
    except Exception as e:
        logger.error(f"Error asking Felix for {user_name}: {e}")
        raise
