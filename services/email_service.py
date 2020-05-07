import os

from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message as MailMessage

from main import mail


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    return serializer.dumps(email, salt=os.environ.get('SECURITY_PASSWORD_SALT'))


def confirm_token(token):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    try:
        email = serializer.loads(token, salt=os.environ.get('SECURITY_PASSWORD_SALT'), max_age=3600)
    except:
        return False
    return email


def send_email(to, subject, template):
    msg = MailMessage(subject, recipients=[to], html=template, sender=os.environ.get('MAIL_DEFAULT_SENDER'))
    mail.send(msg)
