from typing import Callable, Dict, Any, Awaitable
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from config import CHANNEL_ID
import logging

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для предотвращения множественных одновременных запросов"""
    
    def __init__(self):
        self.processing_users = set()
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id из события
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        # Проверяем, обрабатывается ли уже запрос от этого пользователя
        if user_id in self.processing_users:
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⏳ Пожалуйста, дождитесь завершения предыдущего запроса.",
                    show_alert=True
                )
            elif isinstance(event, Message):
                await event.answer(
                    "⏳ Прошу прощения, я ещё обрабатываю ваш предыдущий запрос. "
                    "Позвольте мне завершить, это займёт лишь мгновение."
                )
            return
        
        # Добавляем пользователя в список обрабатываемых
        self.processing_users.add(user_id)
        
        try:
            # Выполняем обработчик
            return await handler(event, data)
        finally:
            # Удаляем пользователя из списка обрабатываемых
            self.processing_users.discard(user_id)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов (rate limiting)"""
    
    def __init__(self, rate_limit: int = 10, period: int = 60):
        self.rate_limit = rate_limit  # максимум запросов
        self.period = period  # период в секундах
        self.user_requests = defaultdict(list)
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        now = datetime.now()
        
        # Очищаем старые запросы
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < timedelta(seconds=self.period)
        ]
        
        # Проверяем лимит
        if len(self.user_requests[user_id]) >= self.rate_limit:
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "⏳ Пожалуйста, подождите немного перед следующим запросом.",
                    show_alert=True
                )
            elif isinstance(event, Message):
                await event.answer(
                    "⏳ Прошу прощения, но Вы отправляете запросы слишком часто.\n\n"
                    "Позвольте мне немного времени для обработки."
                )
            return
        
        # Добавляем текущий запрос
        self.user_requests[user_id].append(now)
        
        return await handler(event, data)


class SubscriptionMiddleware(BaseMiddleware):
    """Middleware для проверки подписки на канал"""
    
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        super().__init__()
    
    async def check_subscription(self, bot: Bot, user_id: int) -> bool:
        """Проверяет подписку пользователя на канал"""
        try:
            member = await bot.get_chat_member(chat_id=self.channel_id, user_id=user_id)
            return member.status in ["member", "administrator", "creator"]
        except TelegramBadRequest:
            logger.warning(f"Не удалось проверить подписку для пользователя {user_id}")
            return True  # Пропускаем, если не можем проверить
        except Exception as e:
            logger.error(f"Ошибка проверки подписки: {e}")
            return True  # Пропускаем при ошибке
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id и bot из события
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            # Пропускаем команду /start для возможности показать сообщение о подписке
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        bot = data.get("bot")
        if not bot:
            return await handler(event, data)
        
        # Проверяем подписку
        is_subscribed = await self.check_subscription(bot, user_id)
        
        if not is_subscribed:
            # Создаём клавиатуру с кнопкой подписки
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{self.channel_id.replace('@', '')}")],
                [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
            ])
            
            message_text = (
                "🎩 *Добро пожаловать в EGOIST ACADEMY*\n\n"
                "Для доступа к академии необходимо подписаться на наш официальный канал.\n\n"
                "После подписки нажмите кнопку «Я подписался»."
            )
            
            if isinstance(event, CallbackQuery):
                # Для callback query отвечаем alert
                if event.data == "check_subscription":
                    # Повторная проверка подписки
                    is_subscribed_now = await self.check_subscription(bot, user_id)
                    if is_subscribed_now:
                        await event.answer("✅ Подписка подтверждена! Добро пожаловать!", show_alert=True)
                        return await handler(event, data)
                    else:
                        await event.answer("❌ Подписка не найдена. Пожалуйста, подпишитесь на канал.", show_alert=True)
                        return
                else:
                    await event.answer("Пожалуйста, подпишитесь на канал для продолжения.", show_alert=True)
                    try:
                        await event.message.answer(message_text, parse_mode="Markdown", reply_markup=keyboard)
                    except:
                        pass
                    return
            elif isinstance(event, Message):
                await event.answer(message_text, parse_mode="Markdown", reply_markup=keyboard)
                return
        
        return await handler(event, data)
