from sqlalchemy import Column, Integer, VARCHAR, ForeignKey

from ...database.models.base import DatabaseModel, TimeStampMixin


class SubCategory(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)

    brand_id = Column(
        Integer,
        ForeignKey("brands.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__sub_categorys_brand_id"),
        nullable=True
    )
    category_id = Column(
        Integer,
        ForeignKey("categorys.id", onupdate="CASCADE", ondelete="CASCADE", name="FK__sub_categorys_category_id"),
        nullable=True
    )

    name = Column(VARCHAR(50))
