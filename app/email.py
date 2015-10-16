from flask.ext.mail import Message
from flask import current_app, render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  sender=current_app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread

