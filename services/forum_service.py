from datetime import datetime, timedelta

from flask_login import current_user

from data import db_session
from data.message import Message
from data.section import Section
from data.thread import Thread
from data.user import User


def create_thr(name, desc, sect_id):
    db = db_session.create_session()
    thread = Thread(name=name, description=desc, author_id=current_user.id,
                    section_id=sect_id, created_date=datetime.now())
    db.add(thread)
    db.commit()
    db.close()


def add_mess(cont, thr_id, ans):
    db = db_session.create_session()
    thread = db.query(Thread).filter(Thread.id == thr_id).first()
    message = Message(content=cont, created_date=datetime.now(), author_id=current_user.id,
                      thread_id=thr_id, answers=ans)
    if message.answers:
        answers_user = db.query(User).filter(User.nickname == message.answers[1:-2]).first()
        message.answers_user_id = answers_user.id

    db.add(message)
    thread.last_message_date = message.created_date
    thread.is_active = True
    db.commit()
    db.close()


def del_thr(thr_id):
    db = db_session.create_session()
    thread = db.query(Thread).filter(Thread.id == thr_id).first()
    messages = db.query(Message).filter(Message.thread_id == thr_id).all()
    for message in messages:
        db.delete(message)
    db.delete(thread)
    db.commit()
    db.close()


def del_mes(mess_id, thr_id):
    db = db_session.create_session()
    thread = db.query(Thread).filter(Thread.id == thr_id).first()
    mess = db.query(Message).filter(Message.id == mess_id).first()
    db.delete(mess)
    thread.count_messages = thread.count_messages - 1
    db.commit()


def edit_mess(mess_id, ans, cont):
    db = db_session.create_session()
    mess = db.query(Message).filter(Message.id == mess_id).first()
    mess.answers = ans
    mess.content = cont
    mess.redact_date = datetime.now()
    db.commit()
    db.close()


def is_active_threads(threads):
    active = 0
    for thread in threads:
        if thread.last_message_date:
            if thread.last_message_date > datetime.now() - timedelta(3):
                active += 1
    return active


def update_threads(threads):
    db = db_session.create_session()
    for thread in threads:
        messages = db.query(Message).filter(Message.thread_id == thread.id).all()
        thread.count_messages = len(messages)
        if messages:
            thread.last_message_date = messages[-1].created_date
        else:
            thread.last_message_date = None
        thread.is_active = bool(is_active_threads([thread]))
    db.commit()
    db.close()


def update_forum():
    db = db_session.create_session()
    sections = db.query(Section).all()
    for sect in sections:
        threads = db.query(Thread).filter(Thread.section_id == sect.id).all()
        sect.count_threads = len(threads)
        if threads:
            sect.last_thread_date = threads[-1].created_date
        else:
            sect.last_thread_date = None
        sect.active_threads = is_active_threads(threads)
    db.commit()
    db.close()