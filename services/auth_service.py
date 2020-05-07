import string
from datetime import date

from flask import session, render_template, url_for

from data import db_session
from data.user import User
from services.email_service import generate_confirmation_token, send_email


def register_error_message(birth_date, captcha, nick, email):
    db = db_session.create_session()
    message = ''

    if birth_date:
        if birth_date > date.today():
            message = "Вы не могли родится в будущем!"
    elif captcha != session['captcha']:
        message = "Капча введена неверно"
    elif [ch for ch in nick if ch not in string.ascii_letters + '1234567890_-/']:
        message = "В нике можно использовать только cимволы a-z, A-Z, 0-9, _-/"
    elif db.query(User).filter(User.email == email).first():
        message = "На эту почту уже зарегистрирован пользователь"
    elif db.query(User).filter(User.nickname == nick).first():
        message = "Пользователь с таким ником уже есть"

    return message


def add_user(birth_date, nick, about, email, password):
    db = db_session.create_session()
    user = User(nickname=nick, about=about, birth_date=birth_date,
                email=email)
    user.set_password(password)
    confirm_url = url_for('confirm_email', token=generate_confirmation_token(user.email), _external=True)
    html = render_template('confirm_account.html', confirm=confirm_url, nick=user.nickname)
    send_email(user.email, "Подтверждение почты на pih-poh.online", html)
    db.add(user)
    db.commit()
