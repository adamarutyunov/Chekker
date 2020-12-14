import datetime
import sqlalchemy.orm as orm
from sqlalchemy import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_session import SqlAlchemyBase
from data import db_session


class UserToLabour(SqlAlchemyBase, SerializerMixin):
    # Модель "пользователь-работа" для связи MTM
    __tablename__ = "user_to_labour"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user = orm.relation('User', backref=orm.backref('labours', lazy='joined', cascade='all'))
    labour_id = Column(Integer, ForeignKey('labours.id'), primary_key=True)
    labour = orm.relation('Labour', backref=orm.backref('performers', lazy='joined', cascade='all'))

    # Количество баллов за работу
    result = Column(Integer, nullable=True)


class UserToTest(SqlAlchemyBase, SerializerMixin):
    # Модель "пользователь-вопрос" для связи MTM
    __tablename__ = "user_to_test"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user = orm.relation('User', backref=orm.backref('tests', lazy='joined', cascade='all'))
    test_id = Column(Integer, ForeignKey('tests.id'), primary_key=True)
    test = orm.relation('Test', backref=orm.backref('testers', lazy='joined', cascade='all'))

    # Выбранный ответ
    chosen_answer = Column(String, nullable=False)
    # Является ли он верным
    is_correct = Column(Boolean, default=False)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    # Модель пользователя
    __tablename__ = 'users'

    # ID пользователя
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Логин
    login = Column(String, nullable=False, unique=True)
    # Отображаемое имя
    name = Column(String, nullable=False)
    # Хэшированный пароль
    hashed_password = Column(String, nullable=True)
    # Роль (уровень доступа)
    role = Column(Integer, default=0)
    # Дата регистрации (сейчас не используется)
    registration_date = Column(DateTime, default=datetime.datetime.now)

    # Установить пароль
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # Проверить пароль
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    # Является ли учителем
    def is_teacher(self):
        return self.role > 0

    # Является ли администратором
    def is_admin(self):
        return self.role > 1

    # Получить МТМ-модель работы
    def get_labour_association(self, labour):
        session = db_session.create_session()

        return session.query(UserToLabour).get((self.id, labour.id))

    # Получить MTM-модель вопроса
    def get_test_association(self, test):
        session = db_session.create_session()

        return session.query(UserToTest).get((self.id, test.id))


class ChekkerAnonymousUser:
    # Класс анонимного пользователя с заглушками. Нужен для внутренней работы Flask-Login
    @property
    def is_active(self):
        return False

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return None

    def set_password(self, password):
        return

    def check_password(self, password):
        return False

    def is_teacher(self):
        return False

    def is_admin(self):
        return False

    def get_labour_association(self, labour):
        return

    def get_test_association(self, test):
        return