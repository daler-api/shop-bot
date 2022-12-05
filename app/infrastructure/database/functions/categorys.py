from typing import List, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from ...database.models import Category


async def add_category(session: AsyncSession, name: str, brand_id: Optional[int], **kwargs) -> Category:
    insert_stmt = select(
        Category
    ).from_statement(
        insert(
            Category
        ).values(
            name=name,
            brand_id=brand_id,
            **kwargs
        ).returning(Category).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_one_category(session: AsyncSession, **kwargs) -> Category:
    statement = select(Category).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_some_categorys(session: AsyncSession, *clauses) -> List[Category]:
    statement = select(
        Category
    ).where(
        *clauses
    ).order_by(
        Category.created_at.asc()
    )
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_count_categorys(session: AsyncSession, *clauses) -> int:
    statement = select(
        func.count(Category.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def update_category(session: AsyncSession, *clauses, **values):
    statement = update(
        Category
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)


async def delete_category(session: AsyncSession, *clauses):
    statement = delete(
        Category
    ).where(
        *clauses
    )
    await session.execute(statement)
