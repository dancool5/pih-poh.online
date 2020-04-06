from flask import Flask, render_template, redirect, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data.user import User
from forms import *
from data import db_session
from captcha.image import ImageCaptcha
import random
import string
import base64

def create_captcha():
    text = ''.join([random.choice(string.ascii_lowercase) for i in range(5)])
    image = ImageCaptcha()
    encode = base64.b64encode(image.generate(text).getvalue())
    return text, encode

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if not form.validate_on_submit():
        captcha_text, encode_captcha = create_captcha()
        session['captcha'] = captcha_text
    else:
        if form.password.data != form.password_again.data:
            captcha_text, encode_captcha = create_captcha()
            session['captcha'] = captcha_text
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают",
                                   сptch=str(encode_captcha)[2:-1])
        if form.captcha.data != session['captcha']:
            captcha_text, encode_captcha = create_captcha()
            session['captcha'] = captcha_text
            return render_template('register.html', title='Регистрация', form=form, message="Капча введена неверно",
                                   сptch=str(encode_captcha)[2:-1])
        db = db_session.create_session()
        if db.query(User).filter(User.email == form.email.data).first():
            captcha_text, encode_captcha = create_captcha()
            session['captcha'] = captcha_text
            return render_template('register.html', title='Регистрация', form=form,
                                   message="На эту почту уже зарегистрирован пользователь",
                                   сptch=str(encode_captcha)[2:-1])
        if db.query(User).filter(User.nickname == form.nickname.data).first():
            captcha_text, encode_captcha = create_captcha()
            session['captcha'] = captcha_text
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пользователь с таким ником уже есть", сptch=str(encode_captcha)[2:-1])
        user = User(nickname=form.nickname.data, about=form.about.data, birth_date=form.birth_date.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.add(user)
        db.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form, сptch=str(encode_captcha)[2:-1])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильная почта или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


db_session.global_init("db/pihpoh_db.sqlite")
if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')