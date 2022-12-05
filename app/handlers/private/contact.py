from aiogram import Router, F
from aiogram.types import CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.functions.infos import get_one_info
from app.keyboards.private.inline import Contact


async def show_contact(c: CallbackQuery, i18n: TranslatorRunner, session: AsyncSession):
    info = await get_one_info(session, name="contact_link")

    link = info.text if info else "t.me/username"

    await c.message.edit_text(
        i18n.contact.text(),
        reply_markup=Contact().get(i18n, link)
    )


def setup(router: Router):
    router.callback_query.register(show_contact, F.data == Contact.cb)
