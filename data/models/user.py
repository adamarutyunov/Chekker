import datetime
import sqlalchemy.orm as orm
from sqlalchemy import *
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_session import SqlAlchemyBase
from data.models.labour import Labour


class UserToLabour(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "user_to_labour"
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user = orm.relation('User', backref=orm.backref('labours', lazy='joined', cascade='all'))
    labour_id = Column(Integer, ForeignKey('labours.id'), primary_key=True)
    labour = orm.relation('Labour', backref=orm.backref('performers', lazy='joined', cascade='all'))
    result = Column(Integer, nullable=True)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    role = Column(Integer, default=0)
    registration_date = Column(DateTime, default=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def is_teacher(self):
        return self.role > 0

    def is_admin(self):
        return self.role > 1


class ChekkerAnonymousUser:
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