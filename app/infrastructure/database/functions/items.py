from typing import List

from sqlalchemy import select, update, delete, func, true
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from ...database.models import Item


async def add_item(
        session: AsyncSession,
        name: str, desc: str, price: int, brand_id: int, category_id: int, sub_category_id: int,
        **kwargs
) -> Item:
    insert_stmt = select(
        Item
    ).from_statement(
        insert(
            Item
        ).values(
            name=name,
            desc=desc,
            price=price,
            brand_id=brand_id,
            category_id=category_id,
            sub_category_id=sub_category_id,
            **kwargs
        ).returning(Item).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def search_items(session: AsyncSession, name: str) -> List[Item]:
    statement = select(
        Item
    ).filter(
        Item.availability == true(),
        func.lower(Item.name).ilike(f'%{name.lower()}%')
    ).order_by(Item.name)
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_one_item(session: AsyncSession, **kwargs) -> Item:
    statement = select(Item).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_some_items(session: AsyncSession, *clauses) -> List[Item]:
    statement = select(
        Item
    ).where(
        *clauses
    ).order_by(
        Item.created_at.desc()
    )
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_pagination_items(session: AsyncSession, offset: int, limit: int, *clauses):
    statement = select(
        Item
    ).where(
        *clauses
    ).order_by(
        Item.id.asc()
    ).offset(offset).limit(limit)
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_count_items(session: AsyncSession, *clauses) -> int:
    statement = select(
        func.count(Item.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def update_item(session: AsyncSession, *clauses, **values):
    statement = update(
        Item
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)


async def delete_item(session: AsyncSession, *clauses):
    statement = delete(
        Item
    ).where(
        *clauses
    )
    await session.execute(statement)
