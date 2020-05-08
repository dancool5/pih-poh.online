from datetime import date

from data import db_session
from data.user import User


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
    user.avatar = avatar
    cash_number = user.cash_number + 1 if user.cash_number < 100 else 0
    user.cash_number = cash_number
    db.commit()
