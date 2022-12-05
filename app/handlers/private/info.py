from aiogram import Router, F
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.functions.infos import get_one_info
from app.keyboards.private.inline import Information, BackInformation


async def show_information(c: CallbackQuery, i18n: TranslatorRunner):
    await c.message.edit_text(
        i18n.info.text(),
        reply_markup=Information().get(i18n)
    )


async def get_info(c: CallbackQuery, callback_data: Information.CD, i18n: TranslatorRunner, session: AsyncSession):
    info = await get_one_info(session, name=callback_data.show)

    text = info.text if info else "—"

    await c.message.edit_text(
        text,
        reply_markup=BackInformation().get(i18n)
    )


def setup(router: Router):
    router.callback_query.register(show_information, Information.CD.filter(F.show == "info"))
    router.callback_query.register(get_info, Information.CD.filter(F.show != "info"))
