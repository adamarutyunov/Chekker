import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase
from data import db_session
from data.models.answer import Answer
from data.models.user import UserToTest


class Attachment(SqlAlchemyBase, SerializerMixin):
    # Модель для вопроса
    __tablename__ = 'attachments'

    # ID вложения
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Вопрос, к которому прикрепляется вложение
    test_id = Column(Integer, ForeignKey("tests.id"))
    test = orm.relation("Test", back_populates="attachments")

    # Тип вложения (см. lib/Attachments.py)
    type = Column(Integer, default=0, nullable=False)

    # Ссылка на вложение
    link = Column(String, nullable=False)
