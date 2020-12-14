from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.widgets import TextArea


class CreateLabourForm(FlaskForm):
    # Форма для создания работы. Повторяет поля БД, см. models/labour.py
    title = StringField('Название', validators=[DataRequired()])
    description = StringField("Описание", widget=TextArea())

    start_date = DateTimeLocalField('Начало', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('Конец', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

    submit = SubmitField('Готово')
