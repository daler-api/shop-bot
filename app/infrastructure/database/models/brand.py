from sqlalchemy import Column, Integer, VARCHAR

from ...database.models.base import DatabaseModel, TimeStampMixin


class Brand(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True)

    name = Column(VARCHAR(50))
