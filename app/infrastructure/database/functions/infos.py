from typing import List

from sqlalchemy import select, update, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from ...database.models import Info


async def add_info(session: AsyncSession, name: str, text: str, **kwargs) -> Info:
    insert_stmt = select(
        Info
    ).from_statement(
        insert(
            Info
        ).values(
            name=name,
            text=text,
            **kwargs
        ).returning(Info).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_one_info(session: AsyncSession, **kwargs) -> Info:
    statement = select(Info).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_some_infos(session: AsyncSession, *clauses) -> List[Info]:
    statement = select(
        Info
    ).where(
        *clauses
    ).order_by(
        Info.created_at.asc()
    )
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_count_infos(session: AsyncSession, *clauses) -> int:
    statement = select(
        func.count(Info.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def update_info(session: AsyncSession, *clauses, **values):
    statement = update(
        Info
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)


async def delete_info(session: AsyncSession, *clauses):
    statement = delete(
        Info
    ).where(
        *clauses
    )
    await session.execute(statement)
