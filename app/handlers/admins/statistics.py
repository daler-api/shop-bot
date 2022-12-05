from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import true
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.functions.users import get_count_users
from app.infrastructure.database.models import User


async def general_stats(m: Message, session: AsyncSession):
    all_users = await get_count_users(session)
    active_users = await get_count_users(session, User.active == true())

    buyers = await get_count_users(session, User.purchase_quantity != 0)
    active_buyers = await get_count_users(session, User.purchase_quantity != 0)

    text = (
        "🌐 <b><i>Общая статистика</i></b>",
        f"👤 <b>Юзеры</b> [всего | актив]: {all_users} | {active_users}",
        f"🛍 <b>Покупатели</b> [всего | актив]: {buyers} | {active_buyers}"
    )
    await m.answer("\n".join(text))


def setup(router: Router):
    router.message.register(general_stats, Command(commands="statistics"))
