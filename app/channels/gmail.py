from threading import Thread

from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipients,subject,  text_body):
    msg = Message(
        sender=('EPA',current_app.config.get("MAIL_USERNAME")),
        subject=subject,
        recipients=recipients,
        body=text_body
    )
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)).start()
