import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy import *
from sqlalchemy_serializer import SerializerMixin
from ..db_session import SqlAlchemyBase
from data import db_session
from data.models.answer import Answer
from data.models.user import UserToTest


class Test(SqlAlchemyBase, SerializerMixin):
    # Модель для вопроса
    __tablename__ = 'tests'

    # ID вопроса
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Работа, в которой находится вопрос
    labour_id = Column(Integer, ForeignKey("labours.id"))
    labour = orm.relation("Labour")

    # Условие вопроса
    statement = Column(String, nullable=False)

    # Тип ответа (подробнее в lib/AnswerTypes.py)
    answer_type = Column(Integer, default=0, nullable=False)

    # Варианты ответа
    answers = orm.relation("Answer", back_populates="test")

    # Вложения
    attachments = orm.relation("Attachment", back_populates="test")

    # Получить все правильные ответы
    def get_correct_answers(self):
        session = db_session.create_session()

        return session.query(Answer).filter((Answer.test == self) & (Answer.is_correct)).all()
