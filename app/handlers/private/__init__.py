from aiogram import Dispatcher, Router, F

from app.handlers.private import start, find_item, info, contact, feedback, search


def setup(dp: Dispatcher):
    router = Router()
    dp.include_router(router)

    router.message.filter(F.chat.type == "private")
    router.callback_query.filter(F.message.chat.type == "private")

    for module in (start, find_item, info, contact, feedback, search):
        module.setup(router)
