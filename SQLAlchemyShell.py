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



session.commit()
