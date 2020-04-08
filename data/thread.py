import datetime
import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import check_password_hash, generate_password_hash


class Thread(SqlAlchemyBase, UserMixin):
    __tablename__ = 'threads'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    section = sqlalchemy.Column(sqlalchemy.String, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    author_nickname = sqlalchemy.Column(sqlalchemy.String, index=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer)
