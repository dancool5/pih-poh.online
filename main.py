import io
from os import path

from flask_mail import Mail

from flask import Flask, redirect, flash, request, send_file, abort, render_template
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta

from data.user import User
from data.section import Section
from data.thread import Thread
from data.message import Message
from forms import *
from data import db_session
from captcha.image import ImageCaptcha
from random import choice
import base64
from dotenv import load_dotenv
import os

from seeder import seed
from services.auth_service import *
from services.email_service import *
from services.forum_service import *
from services.user_service import *


def create_captcha():
    text = ''.join([choice(string.ascii_lowercase) for i in range(5)])
    image = ImageCaptcha()
    encode = base64.b64encode(image.generate(text).getvalue())
    return text, encode


def is_page_exist(obj):
    if not obj:
        return abort(404)


def count_age(birth_date):
    if birth_date:
        # если с момента рождения юзера прошло более 1 года, т.е. пользователю уже есть 1 год
        if datetime.now() - birth_date > timedelta(365):
            # считаем, сколько дней прошло с момента рождения до настоящего времени
            # и делим на 365 (кол-во дней в году) и берем только количество лет
            return str((datetime.now() - birth_date) // 365).split()[0]
        return 0
    return None


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
    update_forum()
    return render_template('forum.html', title='Форум', sections=sections)


@app.route('/forum/section/<section_id>')
def sect(section_id):
    db = db_session.create_session()
    section = db.query(Section).filter(Section.id == section_id).first()
    threads = db.query(Thread).filter(Thread.section_id == section.id).all()
    update_threads(threads)
    threads.reverse()
    return render_template('section.html', title=section.name, threads=threads, section=section)


@app.route('/forum/section/<section_id>/create_thread', methods=['GET', 'POST'])
def create_thread(section_id):
    form = ThreadForm()
    if form.validate_on_submit():
        create_thr(form.name.data, form.description.data, section_id)
        return redirect(url_for('sect', section_id=section_id))
    return render_template('create_thread.html', title='Создать тред', form=form)


@app.route('/forum/section/<section_id>/thread/<thread_id>', methods=['GET', 'POST'])
def thread(section_id, thread_id):
    form = MessageForm()
    db = db_session.create_session()
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    is_page_exist(thread)
    messages = db.query(Message).filter(Message.thread_id == thread.id).all()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return abort(404)
        add_mess(form.content.data, thread.id, form.answers.data)
        return redirect(url_for('thread', thread_id=thread_id, section_id=section_id))

    return render_template('thread.html', thread=thread, messages=messages, form=form, section_id=section_id,
                           title=thread.name)


@app.route('/<thread_id>/delete')
def delete_thread(thread_id):
    db = db_session.create_session()
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    section_id = thread.section_id

    if not current_user.id == thread.author_id:
        return abort(404)

    del_thr(thread_id)
    return redirect(url_for('sect', section_id=section_id))


@app.route('/<section_id>/thread/<thread_id>/message/<message_id>/delete')
def delete_message(thread_id, message_id, section_id):
    db = db_session.create_session()
    message = db.query(Message).filter(Message.id == message_id).first()

    if not current_user.id == message.author_id:
        return abort(404)

    del_mes(message_id, thread_id)
    return redirect(url_for('thread', thread_id=thread_id, section_id=section_id))


@app.route('/<section_id>/thread/<thread_id>/message/<message_id>/edit', methods=['GET', 'POST'])
def edit_message(thread_id, message_id, section_id):
    db = db_session.create_session()
    message = db.query(Message).filter(Message.id == message_id).first()

    if not current_user.id == message.author_id:
        return abort(404)

    form = MessageForm(data={'answers': message.answers, 'content': message.content})
    if form.validate_on_submit():
        edit_mess(message_id, form.answers.data, form.content.data)
        return redirect(url_for('thread', thread_id=thread_id, section_id=section_id))
    return render_template('edit_message.html', title='Редактирование сообщения', form=form, mess=message,
                           thread_id=thread_id, section_id=section_id)


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/donate')
def donate():
    return render_template('donate.html', title='Донат')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        message = register_error_message(form.birth_date.data, form.captcha.data, form.nickname.data, form.email.data)
        if message:
            captcha_text, encode_captcha = create_captcha()
            session['captcha'] = captcha_text
            return render_template('register.html', title='Регистрация', form=form, message=message,
                                   сptch=str(encode_captcha)[2:-1])

        add_user(form.birth_date.data, form.nickname.data, form.about.data, form.email.data, form.password.data)
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


@app.route('/recover', methods=['GET', 'POST'])
def recover_password():
    form = EmailForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(form.email.data == User.email).first()
        if not user:
            return render_template('recover_password.html', message="У нас нет аккаунта с такой почтой", form=form)
        return redirect(url_for('mail_recover_password', user_id=user.id, is_edit=False))
    return render_template('recover_password.html', form=form)


@app.route('/send_mail_to_chng_pass/<user_id>/<is_edit>')
# isedit - переменная для того, чтобы понять, это изменение пароля в edit_page или восстановление пароля
def mail_recover_password(user_id, is_edit):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    is_page_exist(user_id)
    if is_edit == 'True':
        if current_user.id != user.id:
            return abort(404)
    confirm_url = url_for('change_pass', token=generate_confirmation_token(user.email), _external=True)
    html = render_template('mail_recover_pass.html', confirm=confirm_url, nick=user.nickname)
    send_email(user.email, "Смена пароля на pih-poh.online", html)
    flash('На Вашу почту отправлено письмо для смены пароля.', 'success')
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('Ссылка подтверждения недействительна или ее срок действия истек.', 'danger')
    db = db_session.create_session()
    user = db.query(User).filter(User.email == email).first()
    is_page_exist(user)
    if user.is_confirmed:
        flash('Аккаунт уже подтвержден.', 'success')
    else:
        user.is_confirmed = True
        db.add(user)
        db.commit()
        flash('Аккаунт успешно подтвержден!', 'success')
    return redirect('/')


@app.route('/changepass/<token>', methods=['GET', 'POST'])
def change_pass(token):
    try:
        email = confirm_token(token)
    except:
        flash('Ссылка для смены пароля недействительна или ее срок действия истек.', 'danger')
    db = db_session.create_session()
    user = db.query(User).filter(User.email == email).first()
    is_page_exist(user)
    form = PasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.commit()
        flash('Пароль успешно сменен!', 'success')
        return redirect('/')
    return render_template('change_password.html', form=form)



@app.route('/user/<user_id>')
def user(user_id):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    is_page_exist(user)

    user_age = count_age(user.birth_date)
    user_thread = db.query(Thread).filter(Thread.author_id == user_id).all()

    if user_thread:
        user_thread = user_thread[-1]
        update_threads([user_thread])

    if current_user.id == user.id:
        title = 'Моя страница'
    else:
        title = user.nickname
    return render_template('user.html', title=title, user=user, user_age=user_age, thread=user_thread)


@app.route('/user/<user_id>/edit', methods=['GET', 'POST'])
def edit_page(user_id):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    if current_user.id != user.id:
        return abort(404)

    form = EditForm(data={'about': user.about, 'birth_date': user.birth_date})
    if form.validate_on_submit():
        avatar = request.files[form.avatar.name].read() if form.avatar.data else None
        message = edit_page_error_message(form.birth_date.data, avatar)
        if message:
            return render_template('edit_page.html', title='Редактировать страницу', message=message, user=user,
                                   form=form)
        edit_user_page(user_id, form.birth_date.data, form.about.data, avatar)
        return redirect(url_for('user', user_id=user.id))
    return render_template("edit_page.html", title='Редактировать страницу', user=user, form=form)


@app.route('/user/<user_id>/threads')
def all_user_threads(user_id):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    is_page_exist(user)
    user_threads = db.query(Thread).filter(Thread.author_id == user_id).all()
    update_threads(user_threads)
    user_threads.reverse()
    if current_user.id == user.id:
        title = 'Мои треды'
    else:
        title = 'Треды ' + user.nickname
    return render_template('all_threads.html', title=title, user=user, threads=user_threads)


@app.route('/user/<user_id>/avatar/?n=<cash_number>')
def user_avatar(user_id, cash_number):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    if user.avatar:
        return send_file(io.BytesIO(user.avatar), mimetype='image/*')
    return send_file(io.BytesIO(open('static/images/avatar.png', 'rb').read()), mimetype='image/*')


db_session.global_init(path.join(path.dirname(__file__), './db/mars_explorer.db'))

db = db_session.create_session()

if len(db.query(Section).all()) == 0:
    seed()

if __name__ == '__main__':
    app.run(port=os.environ.get('PORT'), host='0.0.0.0')
