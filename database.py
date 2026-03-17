import aiosqlite
import logging
from datetime import datetime
from config import DATABASE_PATH
from constants import ALL_TOPICS, SUBTOPIC_NAMES, TOPIC_NAMES

logger = logging.getLogger(__name__)

async def init_db():
    """Инициализация базы данных с созданием всех необходимых таблиц"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                interests TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                subtopic TEXT NOT NULL,
                content TEXT NOT NULL,
                questions TEXT,
                rating INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                score INTEGER DEFAULT 0,
                liked BOOLEAN DEFAULT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(id),
                UNIQUE(user_id, lesson_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                action_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                source TEXT DEFAULT 'groq',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        logger.info("База данных инициализирована успешно")

async def add_user(telegram_id: int, first_name: str, interests: str, level: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO users (telegram_id, first_name, interests, level) VALUES (?, ?, ?, ?)",
            (telegram_id, first_name, interests, level)
        )
        await db.commit()
        logger.info(f"Пользователь {telegram_id} ({first_name}) добавлен")

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
async def update_user_level(user_id: int, new_level: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))
        await db.commit()

async def save_lesson(user_id: int, topic: str, subtopic: str, content: str, questions: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO lessons (user_id, topic, subtopic, content, questions) VALUES (?, ?, ?, ?, ?)",
            (user_id, topic, subtopic, content, questions)
        )
        await db.commit()
        return cursor.lastrowid

async def get_lesson(lesson_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_lessons(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM lessons WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def add_progress(user_id: int, lesson_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT INTO progress (user_id, lesson_id) VALUES (?, ?)", (user_id, lesson_id))
        await db.commit()

async def update_progress_score(user_id: int, lesson_id: int, score: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE progress SET score = ? WHERE user_id = ? AND lesson_id = ?",
            (score, user_id, lesson_id)
        )
        await db.commit()
        await check_and_update_level(user_id)

async def update_progress_like(user_id: int, lesson_id: int, liked: bool):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE progress SET liked = ? WHERE user_id = ? AND lesson_id = ?",
            (1 if liked else 0, user_id, lesson_id)
        )
        await db.commit()

async def get_user_progress(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                return None
        user_id = user['id']
        async with db.execute('''
            SELECT COUNT(*) as total_lessons,
                   AVG(CASE WHEN score > 0 THEN score ELSE NULL END) as avg_score
            FROM progress WHERE user_id = ?
        ''', (user_id,)) as cursor:
            stats = await cursor.fetchone()
        return {
            'level': user['level'],
            'total_lessons': stats['total_lessons'] or 0,
            'avg_score': round(stats['avg_score'], 1) if stats['avg_score'] else 0
        }
async def check_and_update_level(user_id: int):
    from constants import EXP_PER_LESSON, EXP_PER_LEVEL, MAX_LEVEL
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute('''
            SELECT u.level, COUNT(p.id) as lessons_count
            FROM users u LEFT JOIN progress p ON u.id = p.user_id
            WHERE u.id = ? GROUP BY u.id
        ''', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return
            current_level, lessons_count = row[0], row[1]
        total_exp = lessons_count * EXP_PER_LESSON
        new_level = min(total_exp // EXP_PER_LEVEL + 1, MAX_LEVEL)
        if new_level > current_level:
            await db.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))
            await db.commit()
            logger.info(f'Пользователь {user_id} повышен до уровня {new_level}')

async def add_favorite(user_id: int, lesson_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            await db.execute("INSERT INTO favorites (user_id, lesson_id) VALUES (?, ?)", (user_id, lesson_id))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def remove_favorite(user_id: int, lesson_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM favorites WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
        await db.commit()

async def get_favorites(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT l.id, l.topic, l.subtopic, l.content, f.added_at
            FROM favorites f JOIN lessons l ON f.lesson_id = l.id
            WHERE f.user_id = ? ORDER BY f.added_at DESC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def log_user_action(user_id: int, action_type: str, action_data: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO user_actions (user_id, action_type, action_data) VALUES (?, ?, ?)",
            (user_id, action_type, action_data)
        )
        await db.commit()

async def get_smart_recommendation(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                return None
        interests = user['interests'].split(',')
        async with db.execute('''
            SELECT DISTINCT l.topic, l.subtopic FROM lessons l
            JOIN progress p ON l.id = p.lesson_id WHERE l.user_id = ?
        ''', (user_id,)) as cursor:
            completed = await cursor.fetchall()
            completed_set = {(row['topic'], row['subtopic']) for row in completed}
        async with db.execute('''
            SELECT l.topic, l.subtopic, AVG(p.score) as avg_score, COUNT(*) as attempts
            FROM lessons l JOIN progress p ON l.id = p.lesson_id
            WHERE l.user_id = ? AND p.score > 0
            GROUP BY l.topic, l.subtopic
            HAVING avg_score < 2 AND attempts >= 1
            ORDER BY avg_score ASC LIMIT 1
        ''', (user_id,)) as cursor:
            weak_topic = await cursor.fetchone()
        if weak_topic:
            return {
                'type': 'weak',
                'topic': TOPIC_NAMES.get(weak_topic['topic'], weak_topic['topic']),
                'subtopic': SUBTOPIC_NAMES.get(weak_topic['subtopic'], weak_topic['subtopic']),
                'module': weak_topic['topic'],
                'subtopic_key': weak_topic['subtopic'],
                'reason': f"Средний балл: {weak_topic['avg_score']:.1f}/3. Рекомендую повторить материал."
            }
        for interest in interests:
            if interest in ALL_TOPICS:
                for subtopic_key in ALL_TOPICS[interest]:
                    topic_name = TOPIC_NAMES.get(interest, interest)
                    if (topic_name, subtopic_key) not in completed_set:
                        return {
                            'type': 'new', 'topic': topic_name,
                            'subtopic': SUBTOPIC_NAMES.get(subtopic_key, subtopic_key),
                            'module': interest, 'subtopic_key': subtopic_key,
                            'reason': 'Эта тема соответствует вашим интересам и ещё не изучена.'
                        }
        for module, subtopics in ALL_TOPICS.items():
            for subtopic_key in subtopics:
                topic_name = TOPIC_NAMES.get(module, module)
                if (topic_name, subtopic_key) not in completed_set:
                    return {
                        'type': 'new', 'topic': topic_name,
                        'subtopic': SUBTOPIC_NAMES.get(subtopic_key, subtopic_key),
                        'module': module, 'subtopic_key': subtopic_key,
                        'reason': 'Расширьте свой кругозор, изучив эту тему.'
                    }
        return None
