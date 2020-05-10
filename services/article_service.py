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
