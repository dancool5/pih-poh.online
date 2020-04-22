import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime)
    answers = sqlalchemy.Column(sqlalchemy.String, default=None)
    answers_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    thread_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("threads.id"))
    redact_date = sqlalchemy.Column(sqlalchemy.DateTime, default=None)

    answers_user = orm.relation('User', foreign_keys=[answers_user_id])
    author = orm.relation('User', foreign_keys=[author_id])
    thread = orm.relation('Thread')
