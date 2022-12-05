from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from app.dialogs.states import CategoryEdit


async def show_brands(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(CategoryEdit.brand)


def setup(router: Router):
    router.message.register(show_brands, Command(commands="list"))
