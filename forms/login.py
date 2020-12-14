from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    # Форма для входа в систему.

    # Логин
    login = StringField('Логин', validators=[DataRequired()])

    # Пароль
    password = PasswordField('Пароль', validators=[DataRequired()])

    # Запомнить на 7 дней
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
