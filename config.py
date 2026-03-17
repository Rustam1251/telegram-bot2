import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования для конфига
logger = logging.getLogger(__name__)

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# База данных
DATABASE_PATH = os.getenv("DATABASE_PATH", "academy.db")

# Логирование
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Бэкапы
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")

# Telegram Channel для обязательной подписки
CHANNEL_ID = os.getenv("CHANNEL_ID", "@egoist_academy")

# Валидация обязательных переменных
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен в .env файле!")

# Валидация формата токена (базовая проверка)
if not any(BOT_TOKEN.startswith(str(i)) for i in range(10)):
    raise ValueError("❌ Неверный формат BOT_TOKEN! Токен должен начинаться с цифры.")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY не установлен в .env файле!")

# Валидация формата Groq API ключа
if not GROQ_API_KEY.startswith("gsk_"):
    logger.warning("⚠️ GROQ_API_KEY имеет нестандартный формат. Ожидается префикс 'gsk_'")

logger.info("✅ Конфигурация загружена успешно")

