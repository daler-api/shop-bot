import asyncio
import re
from contextlib import suppress
from operator import attrgetter, itemgetter
from typing import Any

from aiogram import F, Bot, html
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InputMediaPhoto, ContentType, Message
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Group, Button, Select, Back, Row, SwitchTo, Column, ScrollingGroup, Url
from aiogram_dialog.widgets.text import Format, Const
from fluentogram import TranslatorRunner
from sqlalchemy import null, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.constants import re_phone
from app.constants.admin import NEW_ORDER
from app.infrastructure.database.functions.brands import get_some_brands
from app.infrastructure.database.functions.categorys import get_some_categorys
from app.infrastructure.database.functions.items import get_pagination_items, get_one_item, update_item, get_some_items
from app.infrastructure.database.functions.orders import add_order, update_order
from app.infrastructure.database.functions.sub_categorys import get_some_sub_categorys
from app.infrastructure.database.functions.users import update_user
from app.infrastructure.database.models import Category, SubCategory, Item, User, Order
from app.keyboards.private.inline import Menu, BackToMenu
from app.utils.lock_factory import LockFactory
from app.utils.tools import get_mention
from .states import Search
from .utils import FormatTranslate, DynamicMedia


async def on_click_menu(c: CallbackQuery, _, manager: DialogManager):
    i18n: TranslatorRunner = manager.middleware_data["i18n"]

    await manager.done()

    if c.message.content_type == "text":
        with suppress(TelegramAPIError):
            await c.message.edit_text(
                i18n.welcome(
                    channel_link=Config.CHANNEL_LINK
                ),
                reply_markup=Menu().get(i18n),
                disable_web_page_preview=True
            )
    else:
        with suppress(TelegramAPIError):
            await c.message.delete()
        with suppress(TelegramAPIError):
            await c.message.answer(
                i18n.welcome(
                    channel_link=Config.CHANNEL_LINK
                ),
                reply_markup=Menu().get(i18n),
                disable_web_page_preview=True
            )


async def get_data_i18n(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    return {"i18n": i18n}


async def on_click_purchase(_c: CallbackQuery, _select: Any, manager: DialogManager):
    await manager.next()


async def get_data_input_name(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    input_name_err = dialog_manager.dialog_data.get("input_name_err")

    data = {"input_name_err": input_name_err, "i18n": i18n}

    return data


async def func_input_name(m: Message, _, manager: DialogManager):
    if m.text.count(" ") == 0 or len(m.text) > 100:
        manager.dialog_data["input_name_err"] = True
        return

    manager.dialog_data["user_name"] = html.quote(m.text)
    await manager.next()


async def get_data_input_phone(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    input_phone_err = dialog_manager.dialog_data.get("input_phone_err")

    data = {"input_phone_err": input_phone_err, "i18n": i18n}

    return data


async def func_input_phone(m: Message, _, manager: DialogManager):
    if not re.match(re_phone.PATTERN, m.text):
        manager.dialog_data["input_phone_err"] = True
        return

    manager.dialog_data["user_phone"] = html.quote(m.text)
    await manager.switch_to(Search.input_address)


# async def get_data_sdek_point(dialog_manager: DialogManager, **_kwargs):
#     i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
#     session: AsyncSession = dialog_manager.middleware_data["session"]
#
#     sdek_points = await get_some_sdek_points(session)
#
#     return {"items": sdek_points, "i18n": i18n}
#
#
# async def on_click_sdek_point(_c: CallbackQuery, _, manager: DialogManager, item_id: str):
#     session: AsyncSession = manager.middleware_data["session"]
#     manager.dialog_data["sdek_point_id"] = int(item_id)
#
#     sdek_point = await get_one_sdek_point(session, id=int(item_id))
#
#     manager.dialog_data["user_address"] = f"{sdek_point.citi}, {sdek_point.address}"
#
#     await manager.switch_to(Search.input_comment)


async def func_input_address(m: Message, _, manager: DialogManager):
    if len(m.text) > 500:
        manager.dialog_data["input_address_err"] = True
        return

    manager.dialog_data["user_address"] = html.quote(m.text)
    await manager.switch_to(Search.input_comment)


async def func_input_comment(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]

    if len(m.text) > 1000:
        manager.dialog_data["input_comment"] = True
        return

    manager.dialog_data["user_comment"] = html.quote(m.text)

    item_id = manager.start_data["item_id"]
    name = manager.dialog_data["user_name"]
    phone = manager.dialog_data["user_phone"]
    address = manager.dialog_data["user_address"]
    size = manager.start_data["selected_size"]

    order = await add_order(
        session,
        item_id, name, phone, address, size, m.text
    )
    await session.commit()

    manager.dialog_data["order_id"] = order.id

    await manager.next()


async def get_data_order(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    item_id = dialog_manager.start_data["item_id"]

    item = await get_one_item(session, id=item_id)
    item_price = f"{item.price:_}".replace("_", ".")

    data = {
        "i18n": i18n,
        "item": item,
        "item_price": item_price,
        "item_link": item.link if item.link != "-" else "",
        "selected_size": dialog_manager.start_data["selected_size"],
        **dialog_manager.dialog_data
    }
    return data


async def on_click_order(c: CallbackQuery, _, manager: DialogManager):
    i18n: TranslatorRunner = manager.middleware_data["i18n"]
    session: AsyncSession = manager.middleware_data["session"]
    user: User = manager.middleware_data["user_db"]
    lock_factory: LockFactory = manager.middleware_data["lock_factory"]
    bot: Bot = manager.middleware_data["bot"]

    order_id = manager.dialog_data["order_id"]
    item_id = manager.start_data["item_id"]

    phone = manager.dialog_data["user_phone"]
    address = manager.dialog_data["user_address"]
    size = manager.start_data["selected_size"]
    comment = manager.dialog_data["user_comment"]

    async with lock_factory.get_lock("order"):
        item = await get_one_item(session, id=item_id)
        if not item.availability or sum(item.sizes.values()) == 0:
            await manager.switch_to(Search.item_out_stock)
            return
        if item.sizes.get(size, 0) == 0:
            await manager.switch_to(Search.size_out_stock)
            return

        await update_order(
            session,
            Order.id == order_id,
            active=True
        )
        await update_user(
            session,
            User.id == user.id,
            purchase_quantity=user.purchase_quantity + 1
        )

        kwargs = {}

        sizes = item.sizes
        sizes[size] = sizes[size] - 1
        if sum(sizes.values()) == 0:
            kwargs["availability"] = False

        kwargs["sizes"] = sizes

        await update_item(
            session,
            Item.id == item.id,
            **kwargs
        )
        await session.commit()

    text = NEW_ORDER.format(
        order_id=order_id,
        name=get_mention(c.from_user.id, c.from_user.full_name),
        phone=phone,
        address=address,
        item_name=item.name,
        item_link=item.link if item.link != "-" else "",
        size=size,
        price=f"{item.price:_}".replace("_", "."),
        comment=comment
    )

    await bot.send_message(Config.GROUP_ID, text, disable_web_page_preview=True)
    await manager.done()
    await c.message.answer(
        i18n.purchase.order.success(),
        reply_markup=BackToMenu().get(i18n)
    )


async def on_click_delete_purchase(_c: CallbackQuery, _, manager: DialogManager):
    keys = ("input_name_err", "input_phone_err", "input_address_err", "input_comment_err")

    for key in keys:
        with suppress(KeyError):
            del manager.dialog_data[key]


async def get_data_favorite_items(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user_db"]

    len_favorite_items = 0
    items = None
    if user.favorites:
        items = await get_some_items(
            session,
            Item.id.in_(user.favorites)
        )

    if items:
        len_favorite_items = len(items)

    data = {
        "favorite_items": items,
        "len_favorite_items": len_favorite_items,
        "i18n": i18n
    }
    return data


dialog = Dialog(Window(
    FormatTranslate("purchase-item-text"),
    Row(
        Button(
            FormatTranslate("purchase-item-kb"),
            id="purchase",
            on_click=on_click_purchase
        )
    ),
    Row(
        Button(
            FormatTranslate("kb-menu"),
            id="menu",
            on_click=on_click_menu
        )
    ),
    state=Search.purchase,
    getter=get_data_i18n
), Window(
    FormatTranslate("purchase-input_name-text", when=~F["input_name_err"]),
    FormatTranslate("purchase-input_name-err", when=F["input_name_err"]),
    MessageInput(
        func_input_name,
        content_types=ContentType.TEXT
    ),
    getter=get_data_input_name,
    state=Search.input_name
), Window(
    FormatTranslate("purchase-input_phone-text", when=~F["input_phone_err"]),
    FormatTranslate("purchase-input_phone-err", when=F["input_phone_err"]),
    MessageInput(
        func_input_phone,
        content_types=ContentType.TEXT
    ),
    getter=get_data_input_phone,
    state=Search.input_phone
), Window(
    FormatTranslate("purchase-delivery-text"),
    Column(
        SwitchTo(
            FormatTranslate("purchase-sdek-kb"),
            id="delivery_sdek",
            state=Search.sdek_pickup_point
        ),
        SwitchTo(
            FormatTranslate("purchase-address-kb"),
            id="delivery_address",
            state=Search.input_address
        ),
    ),
    getter=get_data_i18n,
    state=Search.select_delivery
    # ), Window(
    #     FormatTranslate("purchase-sdek-text"),
    #     ScrollingGroup(
    #         Select(
    #             Format("{item.citi}, {item.address}"),
    #             id="sdek_point",
    #             items="items",
    #             item_id_getter=attrgetter("id"),
    #             on_click=on_click_sdek_point
    #         ),
    #         id="sdek_points",
    #         width=1,
    #         height=10
    #     ),
    #     getter=get_data_sdek_point,
    #     state=Search.sdek_pickup_point
), Window(
    FormatTranslate("purchase-address-text", when=~F["input_address_err"]),
    FormatTranslate("err-to_long_text", when=F["input_address_err"]),
    Url(
        FormatTranslate("purchase-sdek-kb"),
        url=Const("https://www.cdek.ru/ru/offices"),
        when=~F["input_address_err"]
    ),
    MessageInput(
        func_input_address,
        content_types=ContentType.TEXT
    ),
    getter=get_data_i18n,
    state=Search.input_address
), Window(
    FormatTranslate("purchase-input_comment-text", when=~F["input_comment_err"]),
    FormatTranslate("err-to_long_text", when=F["input_comment_err"]),
    MessageInput(
        func_input_comment,
        content_types=ContentType.TEXT
    ),
    getter=get_data_i18n,
    state=Search.input_comment
), Window(
    FormatTranslate(
        "purchase-order-text",
        {
            "order_id": "{order_id}",
            "name": "{user_name}",
            "phone": "{user_phone}",
            "address": "{user_address}",
            "item_name": "{item.name}",
            "item_link": "{item_link}",
            "size": "{selected_size}",
            "price": "{item_price}",
            "comment": "{user_comment}"
        }
    ),
    Row(
        Button(
            FormatTranslate("purchase-order-kb"),
            id="order",
            on_click=on_click_order
        )
    ),
    Row(
        Button(
            FormatTranslate("kb-menu"),
            id="menu",
            on_click=on_click_menu
        )
    ),
    getter=get_data_order,
    state=Search.place_order
), Window(
    FormatTranslate("purchase-order-item_out_stock-text"),
    Button(
        FormatTranslate("kb-back_menu"),
        id="back_menu",
        on_click=on_click_menu
    ),
    getter=get_data_i18n,
    state=Search.item_out_stock
), Window(
    FormatTranslate("purchase-order-size_out_stock-text"),
    Button(
        FormatTranslate("kb-back_menu"),
        id="back_menu",
        on_click=on_click_menu
    ),
    getter=get_data_i18n,
    state=Search.size_out_stock
)
)
