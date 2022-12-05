from typing import Callable, Dict, Any, Awaitable, Union, Optional

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery, Chat
from fluentogram import TranslatorRunner

from app.services.fluent import FluentService
from app.infrastructure.database import models


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        user_db: Optional[models.User] = data.get("user_db")

        fluent: FluentService = data["fluent"]

        lang = user_db.real_language or "ru"

        translator_runner: TranslatorRunner = fluent.get_translator_by_locale(lang)

        data["i18n"] = translator_runner
        data["i18n_hub"] = fluent.hub
        data["i18n_lang"] = lang
        return await handler(event, data)
