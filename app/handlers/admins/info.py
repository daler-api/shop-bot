from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.functions.infos import update_info, get_one_info, add_info
from app.infrastructure.database.models import Info
from app.keyboards.admin.inline import EditInfo, CancelKb


async def show_edit_information(m: Message, i18n: TranslatorRunner):
    await m.answer(
        "Выберите что вы будите редактировать",
        reply_markup=EditInfo().get(i18n)
    )


async def pre_edit_info(c: CallbackQuery, callback_data: EditInfo.CD, state: FSMContext):
    await state.set_state("edit_info")
    await state.update_data(edit_info=callback_data.show)

    await c.message.edit_text(
        "Теперь напишите текст для этой информации",
        reply_markup=CancelKb().get()
    )


async def edit_info(m: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    name = data["edit_info"]

    await state.set_state(None)

    if await get_one_info(session, name=name):
        await update_info(
            session,
            Info.name == name,
            text=m.html_text
        )
    else:
        await add_info(session, name, m.html_text)
    await session.commit()

    await m.answer("Успешно")


async def pre_edit_contact(m: Message, state: FSMContext):
    await state.set_state("edit_info")
    await state.update_data(edit_info="contact_link")

    await m.answer(
        "Отправьте мне новую ссылку на продавца",
        reply_markup=CancelKb().get()
    )


async def pre_edit_feedback(m: Message, state: FSMContext):
    await state.set_state("edit_info")
    await state.update_data(edit_info="feedback_link")

    await m.answer(
        "Отправьте мне новую ссылку на канал с отзывами",
        reply_markup=CancelKb().get()
    )


def setup(router: Router):
    router.message.register(show_edit_information, Command(commands="edit_info"))
    router.callback_query.register(pre_edit_info, EditInfo.CD.filter())
    router.message.register(edit_info, StateFilter(state="edit_info"))
    router.message.register(pre_edit_contact, Command(commands="edit_contact"))
    router.message.register(pre_edit_feedback, Command(commands="edit_feedback"))
