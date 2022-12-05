from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, false

from ...database.models.base import DatabaseModel, TimeStampMixin


class Order(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)

    item_id = Column(
        Integer,
        ForeignKey("items.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__order_item_id"),
        nullable=True
    )

    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)

    size = Column(String, nullable=False)
    comment = Column(String, nullable=False)

    active = Column(Boolean, server_default=false())
