from flask_wtf import FlaskForm
from wtforms import *
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired
from lib.AnswerTypes import ANSWER_TYPES


class LabourCreateTestForm(FlaskForm):
    # Форма для добавления вопроса к работе.

    # Условие
    statement = StringField("Условие", widget=TextArea(), validators=[DataRequired()])

    # Тип ответа (см. lib/AnswerTypes.py)
    answer_type = SelectField("Тип ответа", coerce=int,
                              choices=list(map(lambda x: (x.id, x.description), ANSWER_TYPES)))

    submit = SubmitField('Готово')
