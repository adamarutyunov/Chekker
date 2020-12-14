import datetime
from data import db_session
from data.models.user import *
from data.models.labour import *
from data.models.test import *
from data.models.answer import *
from Constants import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()

u = User()
u.login = "user"
u.name = "Иван Иванов"
u.role = 0
u.set_password("1")
session.add(u)

session.commit()
