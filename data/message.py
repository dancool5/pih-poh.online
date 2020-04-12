import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Thread(SqlAlchemyBase):
    __tablename__ = 'messages'

    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    author = orm.relation('User')
    thread = orm.relation('Thread')