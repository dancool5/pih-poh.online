import sqlalchemy
from .db_session import SqlAlchemyBase


class Section(SqlAlchemyBase):
    __tablename__ = 'sections'

    name = sqlalchemy.Column(sqlalchemy.String)
    count_threads = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    last_thread_date = sqlalchemy.Column(sqlalchemy.DateTime)