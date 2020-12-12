import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, autoincrement=True)

    test_id = Column(Integer, ForeignKey("tests.id"))
    test = orm.relation("Test")

    data = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
