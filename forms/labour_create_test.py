from flask_wtf import FlaskForm
from wtforms import *
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired


class LabourCreateTestForm(FlaskForm):
    statement = StringField("Условие", widget=TextArea(), validators=[DataRequired()])
    answer_type = SelectField("Тип ответа", coerce=int,
                              choices=[(0, "Ручной ввод"), (1, "Выбор одного ответа"),
                                       (2, "Выбор нескольких ответов")])

    submit = SubmitField('Готово')
