import logging

from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, ContentTypesFilter
from aiogram.types import Message, BotCommandScopeChat, CallbackQuery
from fluentogram import TranslatorRunner

from app.config import Config
from app.keyboards.private.inline import Menu
from app.utils.set_bot_commands import ADMIN_COMMANDS


async def get_start_message(m: Message, bot: Bot, i18n: TranslatorRunner):
    await m.answer(
        i18n.welcome(
            channel_link=Config.CHANNEL_LINK
        ),
        reply_markup=Menu().get(i18n),
        disable_web_page_preview=True
    )

    if str(m.from_user.id) in Config.ADMINS:
        await bot.set_my_commands(ADMIN_COMMANDS, BotCommandScopeChat(chat_id=m.from_user.id))


async def get_menu(c: CallbackQuery, i18n: TranslatorRunner):
    await c.answer()
    await c.message.edit_text(
        i18n.welcome(
            channel_link=Config.CHANNEL_LINK
        ),
        reply_markup=Menu().get(i18n),
        disable_web_page_preview=True
    )


def setup(router: Router):
    router.message.register(get_start_message, CommandStart())
    router.callback_query.register(get_menu, Menu.CD.filter(F.show == "menu"))
