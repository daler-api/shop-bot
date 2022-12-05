from typing import List, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from ...database.models import SubCategory


async def add_sub_category(session: AsyncSession, name: str, brand_id: Optional[int], category_id: Optional[int], **kwargs) -> SubCategory:
    insert_stmt = select(
        SubCategory
    ).from_statement(
        insert(
            SubCategory
        ).values(
            name=name,
            brand_id=brand_id,
            category_id=category_id,
            **kwargs
        ).returning(SubCategory).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_one_sub_category(session: AsyncSession, **kwargs) -> SubCategory:
    statement = select(SubCategory).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_some_sub_categorys(session: AsyncSession, *clauses) -> List[SubCategory]:
    statement = select(
        SubCategory
    ).where(
        *clauses
    ).order_by(
        SubCategory.created_at.asc()
    )
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_count_sub_categorys(session: AsyncSession, *clauses) -> int:
    statement = select(
        func.count(SubCategory.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def update_sub_category(session: AsyncSession, *clauses, **values):
    statement = update(
        SubCategory
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)


async def delete_sub_category(session: AsyncSession, *clauses):
    statement = delete(
        SubCategory
    ).where(
        *clauses
    )
    await session.execute(statement)
