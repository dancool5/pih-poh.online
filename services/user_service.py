from datetime import date
from random import randint

from data import db_session
from data.article import Article
from data.thread import Thread
from data.user import User
from services.forum_service import update_threads


def edit_page_error_message(birth_date, avatar):
    if birth_date:
        if birth_date > date.today():
            return 'Вы не могли родиться в будущем!'
    if avatar:
        if len(avatar) > 1024 * 1024:
            return 'Размер аватара не должен превышать 1Mb'
        # проверка на соответствие расширения файла с допустимыми
        if not [True for extension in ["JFIF", "PNG", "GIF", "WEBP"] if extension in str(avatar)]:
            return 'Допустимые расширения аватара: JEPG, PNG, GIF, WEBP'
    return None


def edit_user_page(user_id, birth_date, about, avatar):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    user.birth_date = birth_date
    user.about = about
    if avatar:
        user.avatar = avatar
    cash_number = randint(1, 10000)
    user.cash_number = cash_number
    db.commit()
    db.close()


def get_user_threads(user_id):
    db = db_session.create_session()
    user_threads = db.query(Thread).filter(Thread.author_id == user_id).all()
    if user_threads:
        user_thread = user_threads[-1]
        update_threads([user_thread])
    else:
        user_thread = None
    return user_thread


def get_user_articles(user_id):
    db = db_session.create_session()
    user_articles = db.query(Article).filter(Article.author_id == user_id).filter(Article.is_admin == False).all()
    if user_articles:
        return user_articles[-1]
    return None
