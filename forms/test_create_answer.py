from flask_wtf import FlaskForm
from wtforms import *
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired


class TestCreateAnswerForm(FlaskForm):
    # Форма для добавления ответа к вопросу

    # Сам ответ
    data = StringField("Ответ", validators=[DataRequired()])

    # Является ли он верным
    is_correct = BooleanField("Это верный ответ?")

    submit = SubmitField('Добавить')
