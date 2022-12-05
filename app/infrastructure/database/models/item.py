import re

from sqlalchemy import Column, Integer, VARCHAR, Boolean, true, ForeignKey, JSON, ARRAY, String

from ...database.models.base import DatabaseModel, TimeStampMixin


class Item(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)

    brand_id = Column(
        Integer,
        ForeignKey("brands.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__item_brand_id"),
        nullable=True
    )
    category_id = Column(
        Integer,
        ForeignKey("categorys.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__item_category_id"),
        nullable=True
    )
    sub_category_id = Column(
        Integer,
        ForeignKey("sub_categorys.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__item_sub_category_id"),
        nullable=True
    )

    name = Column(VARCHAR(100), nullable=False)
    desc = Column(VARCHAR(900), nullable=False)
    price = Column(Integer, nullable=False)

    images = Column(ARRAY(String, True), nullable=False)

    link = Column(VARCHAR(255), nullable=False)

    sizes = Column(JSON, nullable=False)
    availability = Column(Boolean, server_default=true(), nullable=True)

    @property
    def name_normal(self):
        return re.sub(r'\<[^>]*\>', '', self.name)
