import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.dialogs.states import Search
from app.infrastructure.database.functions.items import search_items, get_one_item
from app.infrastructure.database.functions.users import update_user
from app.infrastructure.database.models import User
from app.keyboards.private.inline import Menu, RetrySearch, SearchItem, Favorite, BuyItem


async def search_start(c: CallbackQuery, state: FSMContext):
    await state.set_state("search_input_text")

    await c.message.edit_text("Введите ключевое слово для поиска")


async def search_input_text(m: Message, state: FSMContext, session: AsyncSession, user_db: User, i18n: TranslatorRunner):
    if len(m.text) < 4:
        await m.answer("Поисковый запрос не выполнен, пожалуйста, увеличьте кол-во символов.")
        return

    await state.clear()

    await m.answer("Результат:")

    items = await search_items(session, m.text)
    if not items:
        await m.answer("По вашему запросу ничего не найдено, попробуйте новый запрос", reply_markup=RetrySearch().get())
        return

    for item in items:
        sizes = [(size, count) for size, count in item.sizes.items() if count > 0]
        favorite = item.id in (user_db.favorites or ())

        await m.answer_photo(
            item.images[0],
            f"{item.name}\n{item.desc}",
            reply_markup=SearchItem().get(i18n, sizes, item.id, favorite)
        )
        await asyncio.sleep(0.05)

    await m.answer("Результат поиска", reply_markup=RetrySearch().get())


async def favorite_item(c: CallbackQuery, callback_data: Favorite.CD, user_db: User, session: AsyncSession, i18n: TranslatorRunner):
    item_id = int(callback_data.item_id)

    favorites = user_db.favorites or []
    if item_id in favorites:
        favorite = False
        favorites = (favorite for favorite in favorites if favorite != item_id)
    else:
        favorite = True
        favorites = (*favorites, item_id)

    await update_user(
        session,
        User.id == user_db.id,
        favorites=favorites
    )
    await session.commit()

    item = await get_one_item(session, id=item_id)

    sizes = [(size, count) for size, count in item.sizes.items() if count > 0]

    await c.answer()
    await c.message.edit_reply_markup(SearchItem().get(i18n, sizes, item.id, favorite))


async def select_size(c: CallbackQuery, callback_data: BuyItem.CD, dialog_manager: DialogManager):
    item_id = int(callback_data.item_id)
    size = callback_data.size

    await c.answer()
    await c.message.delete_reply_markup()
    await dialog_manager.start(Search.purchase, {"item_id": item_id, "selected_size": size})


def setup(router: Router):
    router.callback_query.register(search_start, Menu.CD.filter(F.show == "search"))
    router.message.register(search_input_text, state="search_input_text")
    router.callback_query.register(favorite_item, Favorite.CD.filter())
    router.callback_query.register(select_size, BuyItem.CD.filter())
