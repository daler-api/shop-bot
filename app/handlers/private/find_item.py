from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from app.dialogs.states import FindItem
from app.keyboards.private.inline import Menu


async def show_brands(c: CallbackQuery, dialog_manager: DialogManager):
    await c.answer()
    await c.message.delete()

    await dialog_manager.start(FindItem.brand)


async def show_favorites(c: CallbackQuery, dialog_manager: DialogManager):
    await c.answer()
    await c.message.delete()

    await dialog_manager.start(FindItem.favorite)


def setup(router: Router):
    router.callback_query.register(
        show_brands,
        Menu.CD.filter(F.show == "brands")
    )
    router.callback_query.register(
        show_favorites,
        Menu.CD.filter(F.show == "favorites")
    )
