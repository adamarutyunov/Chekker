from flask_wtf import FlaskForm
from wtforms import *
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired


class TestCreateAnswerForm(FlaskForm):
    data = StringField("Ответ", validators=[DataRequired()])
    is_correct = BooleanField("Это верный ответ?")
    submit = SubmitField('Добавить')
