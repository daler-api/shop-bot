from aiogram.filters.state import StatesGroup, State


class BroadcastAdmin(StatesGroup):
    SEND_MESSAGE = State()
    START = State()
