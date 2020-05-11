from datetime import datetime

from flask_login import current_user

from data import db_session
from data.article import Article


def create_art(name, desc):
    db = db_session.create_session()
    article = Article(name=name, description=desc, author_id=current_user.id, created_date=datetime.now())
    db.add(article)
    db.commit()
    db.close()


def del_art(art_id):
    db = db_session.create_session()
    article = db.query(Article).filter(Article.id == art_id).first()
    db.delete(article)
    db.commit()
    db.close()
