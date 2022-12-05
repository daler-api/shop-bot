from aiogram import Router, F
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.functions.infos import get_one_info
from app.keyboards.private.inline import Feedback


async def show_feedback(c: CallbackQuery, i18n: TranslatorRunner, session: AsyncSession):
    info = await get_one_info(session, name="feedback_link")

    link = info.text if info else "t.me/username"

    await c.message.edit_text(
        i18n.feedback.text(),
        reply_markup=Feedback().get(i18n, link)
    )


def setup(router: Router):
    router.callback_query.register(show_feedback, F.data == Feedback.cb)
