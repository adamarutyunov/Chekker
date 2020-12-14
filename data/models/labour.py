import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Labour(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'labours'

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    tests = orm.relation("Test", back_populates="labour")

    start_date = Column(DateTime, default=datetime.datetime.now)
    end_date = Column(DateTime, default=datetime.datetime.now)

    def is_started(self):
        return datetime.datetime.now() >= self.start_date

    def is_finished(self):
        return datetime.datetime.now() >= self.end_date

    def is_active(self):
        return self.is_started() and not self.is_finished()
