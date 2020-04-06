from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, BooleanField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    nickname = StringField('Никнейм', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[Optional()])
    about = TextAreaField("Информация о себе")
    captcha = StringField('')
    submit = SubmitField('Зарегистрироваться')
