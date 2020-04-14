from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, BooleanField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email(message='Неккоректный адрес почты')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль',
                             validators=[DataRequired(), EqualTo('password_again', message='Пароли несовпадают'),
                                         Length(min=5, max=20, message='Пароль должен содержать от 5 до 20 символов')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    nickname = StringField('Никнейм',
                           validators=[DataRequired(), Length(min=3, max=15,
                                                              message='Ник должен содержать от 3 до 15 символов')])
    birth_date = DateField('Дата рождения', validators=[Optional()])
    about = TextAreaField("Информация о себе",
                          validators=[Length(max=100, message='Не пишите слишком много (максимум - 100 символов)!')])
    captcha = StringField('')
    submit = SubmitField('Зарегистрироваться')


class ThreadForm(FlaskForm):
    name = StringField('Тема', validators=[DataRequired(),
                                           Length(max=100, message='Тема должна содержать небольше 100 символов')])
    description = TextAreaField('Описание',
                                validators=[DataRequired(),
                                            Length(max=300, message='Тема должна содержать небольше 300 символов')])
    submit = SubmitField('Создать')
