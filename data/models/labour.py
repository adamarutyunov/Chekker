import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase


class Labour(SqlAlchemyBase, SerializerMixin):
    # Это модель для работы
    __tablename__ = 'labours'

    # Внутренний ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Название работы
    title = Column(String, nullable=False)
    # Описание работы
    description = Column(String, nullable=False)

    # Связь OTM с тестами
    tests = orm.relation("Test", back_populates="labour")

    # Начало работы
    start_date = Column(DateTime, default=datetime.datetime.now)
    # Конец работы
    end_date = Column(DateTime, default=datetime.datetime.now)

    # Метод, проверяющий, началась ли работа
    def is_started(self):
        return datetime.datetime.now() >= self.start_date

    # Метод, проверяющий, закончилась ли работа
    def is_finished(self):
        return datetime.datetime.now() >= self.end_date

    # Метод, проверяющий, доступна ли работа сейчас
    def is_active(self):
        return self.is_started() and not self.is_finished()
