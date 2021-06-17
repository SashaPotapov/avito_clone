from threading import Thread
from flask import current_app, render_template
from flask_login import current_user
from flask_mail import Message
from . import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject=app.config(['FLASKY_MAIL_SUBJECT_PREFIX']) + ' ' + subject, \
                  sender=app.config(['FLASKY_MAIL_SENDER']), \
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(send_async_email)
    thr.start()
    return thr
