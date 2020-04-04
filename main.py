from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional
from data.user import User

from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'QeKT2gpT58HDBr0'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('base.html', title='pih-poh.online')


@app.route('/news_line')
def news_line():
    return render_template('base.html', title='Лента')


@app.route('/forum')
def forum():
    return render_template('base.html', title='Форум')


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/donate')
def donate():
    return render_template('base.html', title='Донат')


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    nickname = StringField('Никнейм', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[Optional()])
    about = TextAreaField("Информация о себе")
    submit = SubmitField('Зарегистрироваться')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db = db_session.create_session()
        if len(db.query(User).filter(User.email == form.email.data).all()) >= 2:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="На эту почту уже зарегистрировано 2 пользователя")
        if db.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пользователь с таким ником уже есть")
        user = User(nickname=form.nickname.data, about=form.about.data, birth_date=form.birth_date.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.add(user)
        db.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


db_session.global_init("db/pihpoh_db.sqlite")
if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')