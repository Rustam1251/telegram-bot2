import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, LOG_FILE, CHANNEL_ID
from database import init_db
from handlers import router
from middleware import ThrottlingMiddleware, RateLimitMiddleware, SubscriptionMiddleware

# Настройка логирования в файл и консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

async def main():
    logging.info("Инициализация базы данных...")
    try:
        await init_db()
        logging.info("База данных инициализирована")
    except Exception as e:
        logging.error(f"Ошибка инициализации базы данных: {e}")
        raise
    
    logging.info("Создание бота...")
    
    # Попытка использовать локальный API сервер или прокси
    try:
        # Вариант 1: Стандартное подключение
        bot = Bot(token=BOT_TOKEN)
    except Exception as e:
        logging.warning(f"Не удалось подключиться напрямую: {e}")
        logging.info("Попытка использовать альтернативный метод...")
        # Можно добавить прокси здесь, если нужно
        bot = Bot(token=BOT_TOKEN)
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем middleware для проверки подписки на канал (первым!)
    dp.message.middleware(SubscriptionMiddleware(channel_id=CHANNEL_ID))
    dp.callback_query.middleware(SubscriptionMiddleware(channel_id=CHANNEL_ID))
    
    # Подключаем middleware для защиты от множественных запросов
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    # Подключаем middleware для rate limiting (10 запросов в минуту)
    dp.message.middleware(RateLimitMiddleware(rate_limit=10, period=60))
    dp.callback_query.middleware(RateLimitMiddleware(rate_limit=10, period=60))
    
    dp.include_router(router)
    
    logging.info("Запуск polling...")
    try:
        await dp.start_polling(bot, skip_updates=False)
    except Exception as e:
        logging.error(f"Ошибка при запуске: {e}")
        logging.info("Проверьте подключение к интернету и доступность api.telegram.org")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        logging.info("Для работы бота требуется доступ к api.telegram.org")
