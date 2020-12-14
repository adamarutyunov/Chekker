import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    # Эта модель репрезентует один ответ, который добавляется к вопросу.

    # ID ответа
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Вопрос, к которому прикрепляется ответ
    test_id = Column(Integer, ForeignKey("tests.id"))
    test = orm.relation("Test")

    # Сам ответ
    data = Column(String, nullable=False)

    # Является ли этот ответ верным
    is_correct = Column(Boolean, default=False, nullable=False)
