import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Thread(SqlAlchemyBase):
    __tablename__ = 'threads'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime)
    last_message_date = sqlalchemy.Column(sqlalchemy.DateTime, default=None)
    count_messages = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=0)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    section_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("sections.id"))

    author = orm.relation('User')
    section = orm.relation('Section')
