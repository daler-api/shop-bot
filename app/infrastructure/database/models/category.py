from sqlalchemy import Column, Integer, VARCHAR, ForeignKey

from ...database.models.base import DatabaseModel, TimeStampMixin


class Category(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)

    brand_id = Column(
        Integer,
        ForeignKey("brands.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__category_brand_id"),
        nullable=True
    )

    name = Column(VARCHAR(50))
