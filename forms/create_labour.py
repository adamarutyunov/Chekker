from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateTimeLocalField


class CreateLabourForm(FlaskForm):
    title = StringField('Название')
    description = StringField("Описание")

    start_date = DateTimeLocalField('Начало', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('Конец', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Готово')
