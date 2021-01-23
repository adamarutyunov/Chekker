import datetime
from data import db_session
from data.models.user import *
from data.models.labour import *
from data.models.test import *
from data.models.answer import *
from Constants import *
from lib.miscellaneous import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()


u = User()
login = generate_login(56, 0, 'e', 1)
print(login)
u.login = login
password = generate_password()
print(password)
u.set_password(password)
u.name = "Елена Теслина"
u.role = 1

session.add(u)

users = session.query(User).all()

for user in users:
    print(user.id, user.name, user.login, user.role)

session.commit()
