import csv
from lib.miscellaneous.passwords import *
from data import db_session
from data.models.user import *
from data.models.labour import *
from data.models.test import *
from data.models.answer import *
from data.models.attachment import *
from Constants import *

db_session.global_init(DATABASE_URI)
session = db_session.create_session()

out = [["№", "Имя", "Логин", "Пароль"]]

with open("lib/miscellaneous/7a.txt", 'rb') as f:
    data = f.read().decode('utf-8')
    lines = data.split("\n")

for line in lines:
    number, name = line.strip().split("\t")
    number = int(number)
    name = name.split()
    name = name[1] + " " + name[0]

    login = generate_login(56, 7, 'a', number)
    password = generate_password(8)

    print(number, name, login, password)

    new_user = User()
    new_user.login = login
    new_user.name = name
    new_user.set_password(password)

    session.add(new_user)
    session.commit()

    out.append([str(number), name, login, password])


teacher_login = generate_login(56, 0, 'o', 1)
teacher_password = generate_password(8)
teacher = User()
teacher.login = teacher_password
teacher.set_password(teacher_password)
teacher.name = "###"
teacher.role = 1

session.add(teacher)
session.commit()


with open('lib/miscellaneous/users.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in out:
        writer.writerow(row)