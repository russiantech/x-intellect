from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from web.extensions import mail

def send_mail(subject, sender, recipients, text_body, html_body):
    def send_async_email(app, msg):
        try:
            with app.app_context():
                mail.send(msg)
                print(f'success, email sent!')
        except Exception as e:
            print(f'Email Error->: {e} | {app.config["MAIL_USERNAME"]}, {app.config["MAIL_PASSWORD"]}')
            return f"{e}"

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    msg.body = text_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

# Example functions using the merged send_mail

def reset_email(user):
    token = user.make_token(token_type="reset_password")
    send_mail(
        '[Techa] . Reset Your Password',
        sender="hackers@techa.tech",
        recipients=[user.email],
        text_body=render_template('email/forgot.txt', user=user, token=token),
        html_body=render_template('email/forgot.html', user=user, token=token)
    )

def verify_email(user):
    token = user.make_token()
    send_mail(
        '[Techa] . Verifications',
        sender="hackers@techa.tech",
        recipients=[user.email],
        text_body=render_template('email/verify.txt', user=user, token=token),
        html_body=render_template('email/verify.html', user=user, token=token)
    )
