from typing import List

from sqlalchemy import select, update, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from ...database.models import Order


async def add_order(
        session: AsyncSession,
        item_id: int, name: str, phone: str, address: str, size: str, comment: str,
        **kwargs
) -> Order:
    insert_stmt = select(
        Order
    ).from_statement(
        insert(
            Order
        ).values(
            item_id=item_id,
            name=name,
            phone=phone,
            address=address,
            size=size,
            comment=comment,
            **kwargs
        ).returning(Order).on_conflict_do_nothing()
    )
    result = await session.scalars(insert_stmt)
    return result.first()


async def get_one_order(session: AsyncSession, **kwargs) -> Order:
    statement = select(Order).filter_by(**kwargs)
    result: AsyncResult = await session.scalars(statement)
    return result.first()


async def get_some_orders(session: AsyncSession, *clauses) -> List[Order]:
    statement = select(
        Order
    ).where(
        *clauses
    ).order_by(
        Order.created_at.desc()
    )
    result: AsyncResult = await session.scalars(statement)
    return result.unique().all()


async def get_count_orders(session: AsyncSession, *clauses) -> int:
    statement = select(
        func.count(Order.id)
    ).where(
        *clauses
    )
    result: AsyncResult = await session.scalar(statement)
    return result


async def update_order(session: AsyncSession, *clauses, **values):
    statement = update(
        Order
    ).where(
        *clauses
    ).values(
        **values
    )
    await session.execute(statement)


async def delete_order(session: AsyncSession, *clauses):
    statement = delete(
        Order
    ).where(
        *clauses
    )
    await session.execute(statement)
