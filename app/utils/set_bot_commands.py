import logging

from aiogram import Bot
from aiogram.types import (
    BotCommand, BotCommandScopeChat, BotCommandScopeAllPrivateChats, BotCommandScopeAllChatAdministrators
)

from app.config import Config
from app.services.fluent import FluentService

PRIVATE_CHAT_COMMANDS = {
    "scope": BotCommandScopeAllPrivateChats(),
    "commands": []
}

ADMIN_CHAT_COMMANDS = {
    "scope": BotCommandScopeAllChatAdministrators(),
    "commands": []
}

ADMIN_COMMANDS = [
    {"command": "statistics", "description": "Общая статистика"},
    {"command": "broadcast", "description": "Рассылка"},
    {"command": "list", "description": "Управление категориями"},
    {"command": "item", "description": "Управление товарами"},
    {"command": "edit_info", "description": "Редактировать информацию"},
    {"command": "edit_contact", "description": "Редактировать контакт"},
    {"command": "edit_feedback", "description": "Редактировать отзывы"}
]

async def set_commands(bot: Bot, fluent: FluentService) -> None:
    await bot.delete_my_commands()

    for lang in fluent.locales_map:
        i18n = fluent.get_translator_by_locale(lang)

        for commands in (PRIVATE_CHAT_COMMANDS, ADMIN_CHAT_COMMANDS):
            cmds = [
                BotCommand(
                    command=cmd["command"],
                    description=i18n.get(cmd["description"])
                )
                for cmd in commands["commands"]
            ]

            try:
                await bot.set_my_commands(cmds, commands["scope"], lang)
            except Exception as err:
                logging.info(err)

    for admin in Config.ADMINS:
        try:
            await bot.set_my_commands(ADMIN_COMMANDS, BotCommandScopeChat(chat_id=admin))
        except Exception as err:
            logging.info(err)
