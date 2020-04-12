import sqlalchemy

from datetime import datetime
from .db_session import SqlAlchemyBase


class Section(SqlAlchemyBase):
    __tablename__ = 'sections'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    address = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    count_threads = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    active_threads = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    last_thread_date = sqlalchemy.Column(sqlalchemy.DateTime, default=None)
