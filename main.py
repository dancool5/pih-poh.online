from flask_mail import Message as MailMessage, Mail

from flask import Flask, render_template, redirect, session, flash, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer

from datetime import date, datetime, timedelta

from data.user import User
from data.section import Section
from data.thread import Thread
from data.message import Message
from forms import *
from data import db_session
from captcha.image import ImageCaptcha
import random
import string
import base64
from dotenv import load_dotenv
import os


def create_captcha():
    text = ''.join([random.choice(string.ascii_lowercase) for i in range(5)])
    image = ImageCaptcha()
    encode = base64.b64encode(image.generate(text).getvalue())
    return text, encode


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except:
        return False
    return email


def send_email(to, subject, template):
    msg = MailMessage(subject, recipients=[to], html=template, sender=app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL') == 'True'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
print(app.config['MAIL_SERVER'],
app.config['MAIL_PORT'],
app.config['MAIL_USE_TLS'],
app.config['MAIL_USE_SSL'],
app.config['MAIL_DEFAULT_SENDER'],
app.config['MAIL_USERNAME'],
app.config['MAIL_PASSWORD'])

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.route('/')
@app.route('/news_line')
def news_line():
    return render_template('base.html', title='Лента')


@app.route('/forum')
def forum():
    db = db_session.create_session()
    sections = db.query(Section).all()
    for sect in sections:
        threads = db.query(Thread).filter(Thread.section_id == sect.id).all()
        active = 0
        for thread in threads:
            if thread.last_message_date:
                if thread.last_message_date < timedelta(3) + datetime.now():
                    active += 1
        sect.active_threads = active
    db.commit()
    return render_template('forum.html', title='Форум', sections=sections)


@app.route('/forum/section/<section_id>')
def sect(section_id):
    db = db_session.create_session()
    section = db.query(Section).filter(Section.id == section_id).first()
    threads = db.query(Thread).filter(Thread.section_id == section.id).all()
    threads.reverse()
    return render_template('section.html', title=section.name, threads=threads, section=section)


@app.route('/forum/section/<section_id>/create_thread', methods=['GET', 'POST'])
def create_thread(section_id):
    form = ThreadForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        thread = Thread(name=form.name.data, description=form.description.data, author_id=current_user.id,
                        section_id=section_id, created_date=datetime.now())
        db.add(thread)
        section = db.query(Section).filter(Section.id == section_id).first()
        section.count_threads = section.count_threads + 1
        section.last_thread_date = thread.created_date
        db.commit()
        return redirect(url_for('sect', section_id=section_id))
    return render_template('create_thread.html', title='Создать тред', form=form)


@app.route('/forum/section/<section_id>/thread/<thread_id>', methods=['GET', 'POST'])
def thread(section_id, thread_id):
    return render_template('base.html')


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/donate')
def donate():
    return render_template('base.html', title='Донат')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    message = ''
    if form.validate_on_submit():
        db = db_session.create_session()
        if form.birth_date.data:
            if form.birth_date.data > date.today():
                message = "Вы не могли родится в будущем!"
        elif form.captcha.data != session['captcha']:
            message = "Капча введена неверно"
        elif db.query(User).filter(User.email == form.email.data).first():
            message = "На эту почту уже зарегистрирован пользователь"
        elif db.query(User).filter(User.nickname == form.nickname.data).first():
            message = "Пользователь с таким ником уже есть"

        if message:
            captcha_text, encode_captcha = create_captcha()
            session['captcha'] = captcha_text
            return render_template('register.html', title='Регистрация', form=form, message=message,
                                   сptch=str(encode_captcha)[2:-1])
        else:
            user = User(nickname=form.nickname.data, about=form.about.data, birth_date=form.birth_date.data,
                        email=form.email.data)
            user.set_password(form.password.data)
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('confirm_account.html', confirm=confirm_url, nick=user.nickname)
            subject = "Подтверждение почты на pih-poh.online"
            send_email(user.email, subject, html)
            db.add(user)
            db.commit()
            flash('На Вашу почту отправлено письмо для подтверждения.', 'success')
            return redirect('/')

    captcha_text, encode_captcha = create_captcha()
    session['captcha'] = captcha_text
    return render_template('register.html', title='Регистрация', form=form, сptch=str(encode_captcha)[2:-1])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_confirmed:
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html', message="Почта аккаунта не подтверждена", form=form)
        return render_template('login.html', message="Неправильная почта или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('Ссылка подтверждения недействительна или ее срок действия истек.', 'danger')
    db = db_session.create_session()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return redirect('/404')
    if user.is_confirmed:
        flash('Аккаунт уже подтвержден.', 'success')
    else:
        user.is_confirmed = True
        db.add(user)
        db.commit()
        flash('Аккаунт успешно подтвержден!', 'success')
    return redirect('/')


db_session.global_init("db/pihpoh_db.sqlite")

db = db_session.create_session()

if len(db.query(Section).all()) == 0:
    sections = {'Русская музыка': ['Описание Описание Описание Описание Описание Описание Описание', 'russian_music'],
                'Зарубежная музыка': ['Описание Описание Описание Описание Описание Описание', 'foreign_music'],
                'Cтихи | поэзия': ['Описание Описание Описание Описание Описание Описание Описание', 'poetry'],
                'Олдскул': ['Описание Описание Описание Описание Описание Описание Описание Описание', 'oldschool'],
                'Фрешмены': ['Описание Описание Описание Описание Описание Описание Описание Описание', 'freshmen'],
                'Битмейкинг': ['Описание Описание Описание Описание Описание Описание Описание Описание', 'beatmaking'],
                'Мероприятия': ['Описание Описание Описание Описание Описание Описание Описание Описание', 'events'],
                'Вопросы новичков': ['Описание Описание Описание Описание Описание Описание', 'novice_questions'],
                'Флуд': ['Описание Описание Описание Описание Описание Описание Описание Описание Описание', 'flood']
                }
    for name, arguments in sections.items():
        description, address = arguments[0], arguments[1]
        section = Section(name=name, description=description, address=address)
        db.add(section)
    db.commit()

if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')
