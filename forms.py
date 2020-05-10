from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, SubmitField, StringField, BooleanField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email(message='Неккоректный адрес почты')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('* Почта', validators=[DataRequired()])
    password = PasswordField('* Пароль',
                             validators=[DataRequired(), EqualTo('password_again', message='Пароли несовпадают'),
                                         Length(min=5, max=20, message='Пароль должен содержать от 5 до 20 символов')])
    password_again = PasswordField('* Повторите пароль', validators=[DataRequired()])
    nickname = StringField('* Никнейм',
                           validators=[DataRequired(), Length(min=3, max=15,
                                                              message='Ник должен содержать от 3 до 15 символов')])
    birth_date = DateField('Дата рождения', validators=[Optional()])
    about = TextAreaField("Информация о себе",
                          validators=[Length(max=100, message='Не пишите слишком много (максимум - 100 символов)!')])
    captcha = StringField('* Капча')
    submit = SubmitField('Зарегистрироваться')


class ThreadForm(FlaskForm):
    name = StringField('Тема', validators=[DataRequired(),
                                           Length(max=100, message='Тема должна содержать неболее 100 символов')])
    description = TextAreaField('Описание',
                                validators=[DataRequired(),
                                            Length(max=300, message='Описание должно содержать неболее 300 символов')])
    submit = SubmitField('Создать')


class MessageForm(FlaskForm):
    answers = StringField('')
    content = TextAreaField('',
                            validators=[DataRequired(), Length(min=1, max=1500,
                                                               message='Сообщение не должно быть пустым' +
                                                                       ' и содержать неболее 1500 символов')])
    submit = SubmitField('Отправить')


class EmailForm(FlaskForm):
    email = StringField('Введите почту, привязанную к Вашему аккаунту',
                        validators=[DataRequired(), Email(message='Неккоректный адрес почты')])
    submit = SubmitField('Отправить')


class PasswordForm(FlaskForm):
    new_password = PasswordField('Новый пароль',
                                 validators=[DataRequired(),
                                             EqualTo('new_password_again', message='Пароли несовпадают'),
                                             Length(min=5, max=20,
                                                    message='Пароль должен содержать от 5 до 20 символов')])
    new_password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Сменить')


class EditForm(FlaskForm):
    avatar = FileField('Сменить аватар')
    birth_date = DateField('Дата рождения', validators=[Optional()])
    about = TextAreaField("Информация о себе",
                          validators=[Length(max=100, message='Не пишите слишком много (максимум - 100 символов)!')])
    submit = SubmitField('Сохранить')


class EmailChangeForm(FlaskForm):
    email = StringField('Введите новую почту',
                        validators=[DataRequired(), Email(message='Неккоректный адрес почты')])
    submit = SubmitField('Отправить')


class ArticleForm(FlaskForm):
    name = StringField('Заголовок', validators=[DataRequired(),
                                           Length(max=100, message='Заголовок должен содержать неболее 100 символов')])
    description = TextAreaField('Статья',
                                validators=[DataRequired(),
                                            Length(max=300, message='Статья должна содержать неболее 3000 символов')])
    submit = SubmitField('Создать')