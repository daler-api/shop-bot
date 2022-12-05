from operator import attrgetter
from typing import Any

from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, ContentType, Message
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Group, Button, Select, Back, Row, SwitchTo, ScrollingGroup
from aiogram_dialog.widgets.text import Format, Const
from fluentogram import TranslatorRunner
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.infrastructure.database.functions.brands import get_some_brands
from app.infrastructure.database.functions.categorys import get_some_categorys
from app.infrastructure.database.functions.items import get_one_item, update_item, get_some_items, \
    get_count_items, delete_item, add_item
from app.infrastructure.database.functions.sub_categorys import get_some_sub_categorys
from app.infrastructure.database.models import Category, SubCategory, Item, User
from .states import ItemActs
from .utils import FormatTranslate, DynamicMedia


async def on_click_close(_c: CallbackQuery, _, manager: DialogManager):
    await manager.done()


async def get_data_i18n(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    return {"i18n": i18n}


async def get_data_brand(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brands = await get_some_brands(session)

    return {"brands": brands}


async def on_click_brand(_c: CallbackQuery, _select: Any, manager: DialogManager, item_id: str):
    manager.dialog_data["brand_id"] = item_id
    await manager.next()


async def get_data_category(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brand_id = dialog_manager.dialog_data["brand_id"]

    categorys = await get_some_categorys(
        session,
        (Category.brand_id == int(brand_id)) if brand_id != "other" else (Category.brand_id.is_(null())),
    )

    return {"categorys": categorys}


async def on_click_category(_c: CallbackQuery, _select: Any, manager: DialogManager, item_id: str):
    manager.dialog_data["category_id"] = item_id
    await manager.next()


async def get_data_sub_category(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brand_id = dialog_manager.dialog_data["brand_id"]
    category_id = dialog_manager.dialog_data["category_id"]

    sub_categorys = await get_some_sub_categorys(
        session,
        (SubCategory.brand_id == int(brand_id)) if brand_id != "other" else (SubCategory.brand_id.is_(null())),
        (SubCategory.category_id == int(category_id)) if category_id != "other" else (SubCategory.category_id.is_(null())),
    )

    return {"sub_categorys": sub_categorys}


async def on_click_sub_category(_c: CallbackQuery, _select: Any, manager: DialogManager, item_id: str):
    session: AsyncSession = manager.middleware_data["session"]
    manager.dialog_data["sub_category_id"] = item_id

    brand_id = manager.dialog_data["brand_id"]
    category_id = manager.dialog_data["category_id"]
    sub_category_id = manager.dialog_data["sub_category_id"]

    items = await get_count_items(
        session,
        (Item.brand_id == int(brand_id)) if brand_id != "other" else (Item.brand_id.is_(null())),
        (Item.category_id == int(category_id)) if category_id != "other" else (Item.category_id.is_(null())),
        (Item.sub_category_id == int(sub_category_id)) if sub_category_id != "other" else (Item.sub_category_id.is_(null())),
        # Item.availability == true()
    )
    if items:
        await manager.switch_to(ItemActs.items)
    else:
        await manager.switch_to(ItemActs.not_found_items)


async def get_data_item(dialog_manager: DialogManager, **_kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user_db"]

    item_id = dialog_manager.dialog_data["item_id"]

    item = await get_one_item(session, id=item_id)

    data = {
        "item": item,
        "name": item.name,
        "desc": item.desc,
        "sizes": ", ".join(list(item.sizes.keys())),
        "price": f"{item.price:_}".replace("_", "."),
        "channel_feedback_username": Config.CHANNEL_FEEDBACK_USERNAME,
        "image_file_id": item.images[0] if item.images else None,
        "item_sizes": [(size, count) for size, count in item.sizes.items() if count > 0],
        "item_favorite": item.id in (user.favorites or ()),
        "show_button_more_image": len(item.images) > 1,
        "more_image_msg_ids": dialog_manager.dialog_data.get("more_image_msg_ids"),
        "offset": dialog_manager.dialog_data.get("offset") is not None
    }

    return data


async def on_click_item(_c: CallbackQuery, _, manager: DialogManager, item_id: str):
    manager.dialog_data["item_id"] = int(item_id)
    await manager.switch_to(ItemActs.item)


async def get_data_items(dialog_manager: DialogManager, **_kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brand_id = dialog_manager.dialog_data["brand_id"]
    category_id = dialog_manager.dialog_data["category_id"]
    sub_category_id = dialog_manager.dialog_data["sub_category_id"]

    items = await get_some_items(
        session,
        (Item.brand_id == int(brand_id)) if brand_id != "other" else (Item.brand_id.is_(null())),
        (Item.category_id == int(category_id)) if category_id != "other" else (Item.category_id.is_(null())),
        (Item.sub_category_id == int(sub_category_id)) if sub_category_id != "other" else (Item.sub_category_id.is_(null())),
        # Item.availability == true()
    )

    return {"items": items}


async def get_data_availability(dialog_manager: DialogManager, **_kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]

    item_id = dialog_manager.dialog_data["item_id"]

    item = await get_one_item(session, id=item_id)

    availability = [f"{size} - {count}" for size, count in item.sizes.items()]

    return {"item": item, "availability": "\n".join(availability)}


async def func_availability(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    new_sizes = {}
    for text in m.text.split("\n"):
        if text.count("-") != 1:
            await m.answer("В тексте ошибка!")
            return

        size, count = text.split("-", maxsplit=1)
        try:
            count = int(count)
        except ValueError:
            await m.answer("В тексте ошибка!")
            return

        new_sizes[size] = count

    await update_item(
        session,
        Item.id == item_id,
        sizes=new_sizes
    )
    await session.commit()


async def func_price(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    try:
        price = int(m.text)
    except ValueError:
        await m.answer("По моему это не цена!")
        return

    await update_item(
        session,
        Item.id == item_id,
        price=price
    )
    await session.commit()


async def func_photo(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    images = (m.photo[0].file_id, )

    await update_item(
        session,
        Item.id == item_id,
        images=images
    )
    await session.commit()

    await m.answer("Готово!")


async def func_name(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    if len(m.html_text) > 100:
        await m.answer("Слишком длинное название!")
        return

    name = m.html_text

    await update_item(
        session,
        Item.id == item_id,
        name=name
    )
    await session.commit()

    await m.answer("Готово!")


async def func_desc(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    if len(m.html_text) > 900:
        await m.answer("Слишком длинное описание!")
        return

    desc = m.html_text

    await m.answer("Проверяем...")
    try:
        await m.answer(desc)
    except TelegramAPIError:
        await m.answer("Ошибка! Уберите из описания символы <, >, &")
        return

    await update_item(
        session,
        Item.id == item_id,
        desc=desc
    )
    await session.commit()

    await m.answer("Готово!")


async def func_link(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    if len(m.text) > 255:
        await m.answer("Слишком длинная ссылка!")
        return

    link = m.text

    await update_item(
        session,
        Item.id == item_id,
        link=link
    )
    await session.commit()

    await m.answer("Готово!")


async def on_click_product_delete(_c: CallbackQuery, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    item_id = manager.dialog_data["item_id"]

    await delete_item(session, Item.id == item_id)
    await session.commit()


async def func_new_item_name(m: Message, _, manager: DialogManager):
    if len(m.html_text) > 100:
        await m.answer("Слишком длинное название для товара")
        return

    manager.dialog_data["new_item_name"] = m.html_text
    await manager.next()


async def func_new_item_desc(m: Message, _, manager: DialogManager):
    if len(m.html_text) > 900:
        await m.answer("Слишком длинное описание для товара")
        return

    await m.answer("Проверяем...")
    try:
        await m.answer(m.html_text)
    except TelegramAPIError:
        await m.answer("Ошибка! Уберите из описания символы <, >, &")
        return

    manager.dialog_data["new_item_desc"] = m.html_text
    await manager.next()


async def func_new_item_photo(m: Message, _, manager: DialogManager):
    manager.dialog_data["new_item_photo"] = (m.photo[0].file_id, )
    await manager.next()


async def func_new_item_availability(m: Message, _, manager: DialogManager):
    new_sizes = {}
    for text in m.text.split("\n"):
        if text.count("-") != 1:
            await m.answer("В тексте ошибка!")
            return

        size, count = text.split("-", maxsplit=1)
        try:
            count = int(count)
        except ValueError:
            await m.answer("В тексте ошибка!")
            return

        new_sizes[size] = count

    manager.dialog_data["new_item_sizes"] = new_sizes
    await manager.next()


async def func_new_item_price(m: Message, _, manager: DialogManager):
    try:
        price = int(m.text)
    except ValueError:
        await m.answer("Это не похоже на число!")
        return

    manager.dialog_data["new_item_price"] = price
    await manager.next()


async def func_new_item_link(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]

    if len(m.text) > 250:
        await m.answer("Слишком длинная ссылка!")
        return

    manager.dialog_data["new_item_link"] = m.text

    name = manager.dialog_data["new_item_name"]
    desc = manager.dialog_data["new_item_desc"]
    photo = manager.dialog_data["new_item_photo"]
    sizes = manager.dialog_data["new_item_sizes"]
    price = manager.dialog_data["new_item_price"]
    link = manager.dialog_data["new_item_link"]

    brand_id = manager.dialog_data["brand_id"]
    category_id = manager.dialog_data["category_id"]
    sub_category_id = manager.dialog_data["sub_category_id"]

    item = await add_item(
        session,
        name=name, desc=desc,
        images=photo, sizes=sizes,
        price=price, link=link,
        brand_id=int(brand_id) if brand_id != "other" else null(),
        category_id=int(category_id) if category_id != "other" else null(),
        sub_category_id=int(sub_category_id) if sub_category_id != "other" else null()
    )
    await session.commit()

    await m.answer("Успешно!")

    manager.dialog_data["item_id"] = item.id
    await manager.switch_to(ItemActs.item)


dialog = Dialog(Window(
    FormatTranslate("brand-text"),
    Group(
        Select(
            Format("{item.name}"),
            id="brand",
            items="brands",
            item_id_getter=attrgetter("id"),
            on_click=on_click_brand
        ),
        id="selection_brand",
        width=2,
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
    ),
    state=ItemActs.brand,
    getter=get_data_brand
), Window(
    FormatTranslate("category-text"),
    Group(
        Select(
            Format("{item.name}"),
            id="category",
            items="categorys",
            item_id_getter=attrgetter("id"),
            on_click=on_click_category
        ),
        id="selection_category",
        width=2
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        Back(FormatTranslate("kb-back"))
    ),
    state=ItemActs.category,
    getter=get_data_category
), Window(
    FormatTranslate("sub_category-text"),
    Group(
        Select(
            Format("{item.name}"),
            id="sub_category",
            items="sub_categorys",
            item_id_getter=attrgetter("id"),
            on_click=on_click_sub_category
        ),
        id="selection_sub_category",
        width=2
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        Back(FormatTranslate("kb-back"))
    ),
    state=ItemActs.sub_category,
    getter=get_data_sub_category
), Window(
    Const("Тут пока что нету товара"),
    Row(
        SwitchTo(
            Const("📦 Добавить новый товар"),
            id="new_item_name",
            state=ItemActs.new_item_name
        )
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        SwitchTo(
            FormatTranslate("kb-back"),
            id="back_sub_categorys",
            state=ItemActs.sub_category
        )
    ),
    state=ItemActs.not_found_items,
    getter=get_data_i18n
), Window(
    Const("Выберите товар"),
    ScrollingGroup(
        Select(
            Format("{item.name_normal}"),
            id="adm_item",
            items="items",
            item_id_getter=attrgetter("id"),
            on_click=on_click_item
        ),
        id="adm_scroll_items",
        width=1,
        height=10
    ),
    Row(
        SwitchTo(
            Const("📦 Добавить новый товар"),
            id="new_item_name",
            state=ItemActs.new_item_name
        )
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        SwitchTo(
            Const("🔙 Назад"),
            id="back_sub_categorys",
            state=ItemActs.sub_category
        )
    ),
    state=ItemActs.items,
    getter=get_data_items
), Window(
    Format("{name}\n{desc}"),
    DynamicMedia(key_in_data="image_file_id", when="image_file_id"),
    Row(
        SwitchTo(
            Const("🔷 Наличие товара"),
            id="product_availability",
            state=ItemActs.availability
        )
    ),
    Row(
        SwitchTo(
            Const("🖊 Изменить цену"),
            id="product_price",
            state=ItemActs.price
        )
    ),
    Row(
        SwitchTo(
            Const("🖼 Изменить фото"),
            id="product_image",
            state=ItemActs.photo
        )
    ),
    Row(
        SwitchTo(
            Const("📌 Изменить название"),
            id="product_name",
            state=ItemActs.name
        )
        ),
    Row(
        SwitchTo(
            Const("📎 Изменить описание"),
            id="product_desc",
            state=ItemActs.desc
        )
    ),
    Row(
        SwitchTo(
            Const("🔗 Изменить ссылку"),
            id="product_link",
            state=ItemActs.link
        )
    ),
    Row(
        SwitchTo(
            Const("⛔ Удалить товар"),
            id="product_delete",
            state=ItemActs.items,
            on_click=on_click_product_delete
        )
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_items",
            state=ItemActs.items
        )
    ),
    state=ItemActs.item,
    getter=get_data_item
), Window(
    Format(
        "Сейчас наличие товара такое:\n"
        "<code>{availability}</code>\n"
        "Вы можете скопировать этот текст и изменять значения или добавить новые."
    ),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_item",
        state=ItemActs.item
    ),
    MessageInput(
        func_availability,
        ContentType.TEXT
    ),
    state=ItemActs.availability,
    getter=get_data_availability
), Window(
    Format(
        "Сейчас цена товара: {price}\n"
        "Вы можете написать новую цену товара."
    ),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_item",
        state=ItemActs.item
    ),
    MessageInput(
        func_price,
        ContentType.TEXT
    ),
    state=ItemActs.price,
    getter=get_data_item
), Window(
    Const("Вы можете отправить мне новое фото для товара."),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_item",
        state=ItemActs.item
    ),
    MessageInput(
        func_photo,
        ContentType.PHOTO
    ),
    state=ItemActs.photo
), Window(
    Const("Вы можете написать новое название для товара"),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_item",
        state=ItemActs.item
    ),
    MessageInput(
        func_name,
        ContentType.TEXT
    ),
    state=ItemActs.name
), Window(
    Const("Вы можете написать новое описание для товара"),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_item",
        state=ItemActs.item
    ),
    MessageInput(
        func_desc,
        ContentType.TEXT
    ),
    state=ItemActs.desc
), Window(
    Format("Вы можете написать новую ссылку для товара\nСейчас стоит: {item.link}"),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_item",
        state=ItemActs.item
    ),
    MessageInput(
        func_link,
        ContentType.TEXT
    ),
    getter=get_data_item,
    state=ItemActs.link
), Window(
    Const("Напишите название для нового товара"),
    SwitchTo(
        Const("⛔ Отменить"),
        id="back_to_item",
        state=ItemActs.items
    ),
    MessageInput(
        func_new_item_name,
        ContentType.TEXT
    ),
    state=ItemActs.new_item_name
), Window(
    Const("Напишите описание для нового товара"),
    SwitchTo(
        Const("⛔ Отменить"),
        id="back_to_item",
        state=ItemActs.items
    ),
    MessageInput(
        func_new_item_desc,
        ContentType.TEXT
    ),
    state=ItemActs.new_item_desc
), Window(
    Const("Отправьте фото для нового товара"),
    SwitchTo(
        Const("⛔ Отменить"),
        id="back_to_item",
        state=ItemActs.items
    ),
    MessageInput(
        func_new_item_photo,
        ContentType.PHOTO
    ),
    state=ItemActs.new_item_photo
), Window(
    Const(
        "Отправьте размеры и их количество для нового товара\n"
        "Пример:\n"
        "<code>S - 10\n"
        "XXL - 20</code>"
    ),
    SwitchTo(
        Const("⛔ Отменить"),
        id="back_to_item",
        state=ItemActs.items
    ),
    MessageInput(
        func_new_item_availability,
        ContentType.TEXT
    ),
    state=ItemActs.new_item_availability
), Window(
    Const("Отправьте цену для нового товара"),
    SwitchTo(
        Const("⛔ Отменить"),
        id="back_to_item",
        state=ItemActs.items
    ),
    MessageInput(
        func_new_item_price,
        ContentType.TEXT
    ),
    state=ItemActs.new_item_price
), Window(
    Const("Отправьте ссылку на товар из канала\nНапишите - если ссылка не нужна"),
    SwitchTo(
        Const("⛔ Отменить"),
        id="back_to_item",
        state=ItemActs.items
    ),
    MessageInput(
        func_new_item_link,
        ContentType.TEXT
    ),
    state=ItemActs.new_item_link
))
