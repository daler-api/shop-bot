from dataclasses import dataclass
from operator import attrgetter

from aiogram.types import CallbackQuery, ContentType, Message
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Group, Button, Select, Back, Row, \
    SwitchTo
from aiogram_dialog.widgets.text import Format, Const
from fluentogram import TranslatorRunner
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.functions.brands import get_some_brands, add_brand, get_one_brand, delete_brand, \
    update_brand
from app.infrastructure.database.functions.categorys import get_some_categorys, add_category, get_one_category, \
    delete_category, update_category
from app.infrastructure.database.functions.sub_categorys import get_some_sub_categorys, add_sub_category, \
    delete_sub_category, get_one_sub_category, update_sub_category
from app.infrastructure.database.models import Category, SubCategory, Brand
from .states import CategoryEdit
from .utils import FormatTranslate


async def on_click_close(_c: CallbackQuery, _, manager: DialogManager):
    await manager.done()


async def get_data_brand(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brands = await get_some_brands(session)

    return {"brands": brands}


async def on_click_brand(_c: CallbackQuery, _, manager: DialogManager, item_id: str):
    manager.dialog_data["brand_id"] = item_id
    await manager.next()


async def get_data_category(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brand_id = dialog_manager.dialog_data["brand_id"]

    if brand_id != "other":
        brand = await get_one_brand(session, id=int(brand_id))
    else:
        brand = None

    categorys = await get_some_categorys(
        session,
        (Category.brand_id == int(brand_id)) if brand_id != "other" else (Category.brand_id.is_(null()))
    )

    return {"categorys": categorys}


async def on_click_category(_c: CallbackQuery, _, manager: DialogManager, item_id: str):
    manager.dialog_data["category_id"] = item_id
    await manager.next()


async def get_data_sub_category(dialog_manager: DialogManager, **_kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    session: AsyncSession = dialog_manager.middleware_data["session"]

    brand_id = dialog_manager.dialog_data["brand_id"]
    category_id = dialog_manager.dialog_data["category_id"]

    if category_id != "other":
        category = await get_one_category(session, id=int(category_id))
    else:
        category = None

    sub_categorys = await get_some_sub_categorys(
        session,
        (SubCategory.brand_id == int(brand_id)) if brand_id != "other" else (SubCategory.brand_id.is_(null())),
        (SubCategory.category_id == int(category_id)) if category_id != "other" else (SubCategory.category_id.is_(null()))
    )

    return {"sub_categorys": sub_categorys, "category": category}


async def on_click_sub_category(_c: CallbackQuery, _, manager: DialogManager, item_id: str):
    manager.dialog_data["sub_category_id"] = item_id

    if item_id != "other":
        await manager.switch_to(CategoryEdit.edit_sub_category)


async def func_add_new_brand(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]

    brand = await get_some_brands(session, Brand.name.ilike(f"%{m.text}%"))
    if brand:
        await m.answer("Ошибка, такой бренд уже существует!")
        return

    await add_brand(session, m.text)
    await session.commit()

    await m.answer(f"Бренд под названием «{m.text}» добавлен успешно")
    await manager.switch_to(CategoryEdit.brand)


async def func_add_new_category(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    brand_id = manager.dialog_data["brand_id"]

    category = await get_some_categorys(
        session,
        (Category.brand_id == int(brand_id)) if brand_id != "other" else (Category.brand_id.is_(null())),
        Category.name.ilike(f"%{m.text}%")
    )
    if category:
        await m.answer("Ошибка, такая категория в этом бренде уже существует!")
        return

    await add_category(
        session,
        m.text, int(brand_id) if brand_id != "other" else null()
    )
    await session.commit()

    await m.answer(f"Категория под названием «{m.text}» в этом бренде добавлен успешно")
    await manager.switch_to(CategoryEdit.category)


async def func_add_new_sub_category(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]

    brand_id = manager.dialog_data["brand_id"]
    category_id = manager.dialog_data["category_id"]

    sub_category = await get_some_sub_categorys(
        session,
        (SubCategory.brand_id == int(brand_id)) if brand_id != "other" else (SubCategory.brand_id.is_(null())),
        (SubCategory.category_id == int(category_id)) if category_id != "other" else (SubCategory.category_id.is_(null())),
        SubCategory.name.ilike(f"%{m.text}%")
    )
    if sub_category:
        await m.answer("Ошибка, такая подкатегория в этой категории уже существует!")
        return

    await add_sub_category(
        session,
        m.text, int(brand_id), int(category_id) if category_id != "other" else null()
    )
    await session.commit()

    await m.answer(f"Подкатегория под названием «{m.text}» в этой категории добавлен успешно")
    await manager.switch_to(CategoryEdit.sub_category)


async def get_data_edit_brand(dialog_manager: DialogManager, **_kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    brand_id = dialog_manager.dialog_data["brand_id"]

    brand = await get_one_brand(session, id=int(brand_id))

    return {"brand": brand}


async def func_edit_name_brand(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    brand_id = manager.dialog_data["brand_id"]

    await update_brand(
        session,
        Brand.id == int(brand_id),
        name=m.text
    )
    await session.commit()

    await manager.switch_to(CategoryEdit.edit_brand)


async def on_click_delete_brand(_c: CallbackQuery, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    brand_id = manager.dialog_data["brand_id"]

    await delete_brand(session, Brand.id == int(brand_id))
    await session.commit()


async def get_data_edit_category(dialog_manager: DialogManager, **_kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    category_id = dialog_manager.dialog_data["category_id"]

    category = await get_one_category(session, id=int(category_id))

    return {"category": category}


async def func_edit_name_category(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    category_id = manager.dialog_data["category_id"]

    await update_category(
        session,
        Category.id == int(category_id),
        name=m.text
    )
    await session.commit()

    await manager.switch_to(CategoryEdit.edit_category)


async def on_click_delete_category(_c: CallbackQuery, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    category_id = manager.dialog_data["category_id"]

    await delete_category(session, Category.id == int(category_id))
    await session.commit()


async def get_data_edit_sub_category(dialog_manager: DialogManager, **_kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    sub_category_id = dialog_manager.dialog_data["sub_category_id"]

    sub_category = await get_one_sub_category(session, id=int(sub_category_id))

    return {"sub_category": sub_category}


async def func_edit_name_sub_category(m: Message, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    sub_category_id = manager.dialog_data["sub_category_id"]

    await update_sub_category(
        session,
        SubCategory.id == int(sub_category_id),
        name=m.text
    )
    await session.commit()

    await manager.switch_to(CategoryEdit.edit_sub_category)


async def on_click_delete_sub_category(_c: CallbackQuery, _, manager: DialogManager):
    session: AsyncSession = manager.middleware_data["session"]
    sub_category_id = manager.dialog_data["sub_category_id"]

    await delete_sub_category(session, SubCategory.id == int(sub_category_id))
    await session.commit()


dialog = Dialog(Window(
    FormatTranslate("brand-text"),
    Group(
        Select(
            Format("{item.name}"),
            id="act_brand",
            items="brands",
            item_id_getter=attrgetter("id"),
            on_click=on_click_brand
        ),
        id="act_selection_brand",
        width=2,
    ),
    Row(
        SwitchTo(
            Const("➕ Добавить новый каталог"),
            id="add_new_brand",
            state=CategoryEdit.add_new_brand
        )
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        )
    ),
    state=CategoryEdit.brand,
    getter=get_data_brand
), Window(
    FormatTranslate("category-text"),
    Group(
        Select(
            Format("{item.name}"),
            id="act_category",
            items="categorys",
            item_id_getter=attrgetter("id"),
            on_click=on_click_category
        ),
        id="act_selection_category",
        width=2
    ),
    Row(
        SwitchTo(
            Const("➕ Добавить новую категорию"),
            id="add_new_brand",
            state=CategoryEdit.add_new_category
        )
    ),
    Row(
        SwitchTo(
            Format("⚙ Ред. каталог «{brand.name}»"),
            id="edit_brand",
            state=CategoryEdit.edit_brand,
            when="brand"
        )
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        Back(FormatTranslate("kb-back"))
    ),
    state=CategoryEdit.category,
    getter=get_data_category
), Window(
    FormatTranslate("sub_category-text"),
    Group(
        Select(
            Format("{item.name}"),
            id="act_sub_category",
            items="sub_categorys",
            item_id_getter=attrgetter("id"),
            on_click=on_click_sub_category
        ),
        id="act_selection_sub_category",
        width=2
    ),
    Row(
        SwitchTo(
            Const("➕ Добавить новую подкатегорию"),
            id="add_new_brand",
            state=CategoryEdit.add_new_sub_category
        )
    ),
    Row(
        SwitchTo(
            Format("⚙ Ред. категорию «{category.name}»"),
            id="edit_category",
            state=CategoryEdit.edit_category,
            when="category"
        )
    ),
    Row(
        Button(
            Const("❌ Закрыть"),
            id="close",
            on_click=on_click_close
        ),
        Back(FormatTranslate("kb-back"))
    ),
    state=CategoryEdit.sub_category,
    getter=get_data_sub_category
), Window(
    Const("Напишите название нового бренда"),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_brands",
        state=CategoryEdit.brand
    ),
    MessageInput(
        func_add_new_brand,
        ContentType.TEXT
    ),
    state=CategoryEdit.add_new_brand
), Window(
    Const("Напишите название новой категории"),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_categorys",
        state=CategoryEdit.category
    ),
    MessageInput(
        func_add_new_category,
        ContentType.TEXT
    ),
    state=CategoryEdit.add_new_category
), Window(
    Const("Напишите название новой подкатегории"),
    SwitchTo(
        Const("🔙 Назад"),
        id="back_to_sub_categorys",
        state=CategoryEdit.sub_category
    ),
    MessageInput(
        func_add_new_sub_category,
        ContentType.TEXT
    ),
    state=CategoryEdit.add_new_sub_category
), Window(
    Format("Редактирование бренда «{brand.name}»"),
    Row(
        SwitchTo(
            Const("✏ Изменить название"),
            id="edit_name_brand",
            state=CategoryEdit.edit_name_brand
        )
    ),
    Row(
        SwitchTo(
            Const("❌ Удалить"),
            id="delete_brand",
            state=CategoryEdit.brand,
            on_click=on_click_delete_brand
        )
    ),
    Row(
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_brands",
            state=CategoryEdit.brand
        )
    ),
    getter=get_data_edit_brand,
    state=CategoryEdit.edit_brand
), Window(
    Format("Напишите новое название для бренда «{brand.name}»"),
    Row(
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_edit_brand",
            state=CategoryEdit.edit_brand
        )
    ),
    MessageInput(
        func_edit_name_brand,
        ContentType.TEXT
    ),
    getter=get_data_edit_brand,
    state=CategoryEdit.edit_name_brand
), Window(
    Format("Редактирование категории «{category.name}»"),
    Row(
        SwitchTo(
            Const("✏ Изменить название"),
            id="edit_name_category",
            state=CategoryEdit.edit_name_category
        )
    ),
    Row(
        SwitchTo(
            Const("❌ Удалить"),
            id="delete_category",
            state=CategoryEdit.category,
            on_click=on_click_delete_category
        )
    ),
    Row(
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_categorys",
            state=CategoryEdit.category
        )
    ),
    getter=get_data_edit_category,
    state=CategoryEdit.edit_category
), Window(
    Format("Напишите новое название для категории «{category.name}»"),
    Row(
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_edit_category",
            state=CategoryEdit.edit_category
        )
    ),
    MessageInput(
        func_edit_name_category,
        ContentType.TEXT
    ),
    getter=get_data_edit_category,
    state=CategoryEdit.edit_name_category
), Window(
    Format("Редактирование подкатегории «{sub_category.name}»"),
    Row(
        SwitchTo(
            Const("✏ Изменить название"),
            id="edit_name_sub_category",
            state=CategoryEdit.edit_name_sub_category
        )
    ),
    Row(
        SwitchTo(
            Const("❌ Удалить"),
            id="delete_sub_category",
            state=CategoryEdit.sub_category,
            on_click=on_click_delete_sub_category
        )
    ),
    Row(
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_sub_categorys",
            state=CategoryEdit.sub_category
        )
    ),
    getter=get_data_edit_sub_category,
    state=CategoryEdit.edit_sub_category
), Window(
    Format("Напишите новое название для подкатегории «{sub_category.name}»"),
    Row(
        SwitchTo(
            Const("🔙 Назад"),
            id="back_to_edit_sub_category",
            state=CategoryEdit.edit_sub_category
        )
    ),
    MessageInput(
        func_edit_name_sub_category,
        ContentType.TEXT
    ),
    getter=get_data_edit_sub_category,
    state=CategoryEdit.edit_name_sub_category
)
)
