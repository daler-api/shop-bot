from typing import List

from sqlalchemy import select, update, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from ...database.models import Brand


async def add_brand(session: AsyncSession, name: str, **kwargs) -> Brand:
    insert_stmt = select(
        Brand
    ).from_statement(
        insert(
            Brand
        ).values(
            name=name,
            **kwargs
        ).returning(Brand).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_one_brand(session: AsyncSession, **kwargs) -> Brand:
    statement = select(Brand).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_some_brands(session: AsyncSession, *clauses) -> List[Brand]:
    statement = select(
        Brand
    ).where(
        *clauses
    ).order_by(
        Brand.created_at.asc()
    )
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_count_brands(session: AsyncSession, *clauses) -> int:
    statement = select(
        func.count(Brand.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def update_brand(session: AsyncSession, *clauses, **values):
    statement = update(
        Brand
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)


async def delete_brand(session: AsyncSession, *clauses):
    statement = delete(
        Brand
    ).where(
        *clauses
    )
    await session.execute(statement)
