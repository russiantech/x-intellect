from datetime import datetime
from flask import abort, jsonify, render_template, url_for, flash, redirect, request, Blueprint
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required
#from utils.time_ago import timeAgo
from web.extensions import bcrypt, mail
from web.models import db, User, Notification

from web.utils import save_image, email, time_ago, ip_adrs
from web.auth.forms import (SignupForm, SigninForm, UpdateMeForm, ForgotForm, ResetForm)

auth = Blueprint('auth', __name__)

@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, 
                    ip =ip_adrs.user_ip())
        db.session.add(user)
        db.session.commit()
        email.verify_email(user) if user else flash('Undefined User.', 'info')
        flash('Your Account Has Been Created! You Are Now Able To Log In', 'success')
        return redirect(url_for('auth.signin'))
    return render_template('auth/signup.html', title='Sign-up', form=form)


@auth.route("/signin", methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            current_user.online = True
            current_user.last_seen = datetime.utcnow()
            current_user.ip = ip_adrs.user_ip()
            current_user.notify(f'unread', f'Recent Signin -> {time_ago.timeAgo(current_user.last_seen)}')
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.user'))
        else:
            flash('Invalid Login Details. Try Again', 'danger')
    return render_template('auth/signin.html', title='Sign In', form=form)

@auth.route("/signout")
@login_required
def signout():
    logout_user()
    current_user.online = False
    db.session.commit()
    return redirect(url_for('main.welcome'))

@auth.route("/<string:usrname>/update", methods=['GET', 'POST'])
#@auth.route("/update/<string:usrname>", methods=['GET', 'POST'])
@login_required
def update(usrname):
    user = User.query.filter_by(username=usrname).first_or_404()
    if ( (current_user.is_admin()) | (current_user.username == user.username) ):
        form = UpdateMeForm()
        if form.validate_on_submit(): 
            #user.photo = save_image.save_photo(form.photo.data) if form.photo.data else current_user.photo or 'default.svg'
            user.image = save_image.save_photo(form.image.data) or current_user.image or 'default.webp'
            user.name = form.name.data
            user.username = form.username.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.gender = form.gender.data
            user.lang = form.lang.data
            user.city = form.city.data
            user.about = form.about.data
            user.duration = form.time.data or 0
            #user.socials = form.socials.data
            db.session.commit()
            flash('Your Account Has Been Updated!', 'success')
            return redirect(url_for('main.user'))
        elif request.method == 'GET':
            form.image.data = user.image
            form.name.data = user.name
            form.username.data = user.username
            form.email.data = user.email
            form.phone.data = user.phone
            form.gender.data = user.gender
            form.lang.data = user.lang
            form.city.data = user.city
            form.about.data = user.about
            form.time.data = user.duration or 0 #default
            #form.socials.data = user.socials
        return render_template('auth/update.html', photo=user.image, form=form)
    return redirect(url_for('auth.update', usrname=current_user.username))

@auth.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        email.reset_email(user) if user else flash('Undefined User.', 'info')
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.signin'))
    elif request.method == 'GET':
        form.email.data = request.args.get('e')
    return render_template('auth/forgot.html', form=form)

#->for unverified-users, notice use of 'POST' instead of 'post' before it works
@auth.route("/unverified", methods=['post', 'get'])
@login_required
def unverified():
    if request.method == 'POST':
        email.verify_email(current_user)
        flash('Verication Emails Sent Again, Check You Mail Box', 'info')
    return render_template('auth/unverified.html')

#->for both verify/reset tokens
@auth.route("/confirm/<token>", methods=['GET', 'POST'])
def confirm(token):
    print(current_user.generate_token(type='verify'))
    if current_user.is_authenticated:
        print(current_user.generate_token(type='verify')) #generate-token
        return redirect(url_for('main.welcome'))
    
    conf = User.verify_token(token) #verify

    if not conf:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.signin'))
    
    user = conf[0] 
    type = conf[1]

    if not user :
        flash('Invalid/Expired Token', 'warning')
        return redirect(url_for('main.welcome'))
    
    if type == 'verify' and user.verified == True:
        flash(f'Weldone {user.username}, you have done this before now', 'success')
        return redirect(url_for('auth.signin', _external=True))

    if type == 'verify' and user.verified == False:
        user.verified = True
        db.session.commit()
        flash(f'Weldone {user.username}, Your Email Address is Confirmed, Continue Here', 'success')
        return redirect(url_for('auth.signin', _external=True))

    if type == 'reset':
        form = ResetForm() 
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated! Continue', 'success')
            return redirect(url_for('auth.signin'))
        return render_template('auth/reset.html', user=user, form=form)

@auth.route('/notify')
@login_required
def notify():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(Notification.created > since).order_by(Notification.created.asc())
    return jsonify([{ 'name': n.name, 'data': n.get_data(), 'timestamp': n.created } for n in notifications])


@auth.route("/test_tokens/<email>", methods=['GET', 'POST'])
def test_tokens(email):
    u = User.query.filter_by(email=email)
    if u:
        tk = u.generate_token(type='verify')
        print(tk) #generate-token
        #return redirect(url_for('main.welcome'))
    conf = User.verify_token(tk) #verify

    if not conf:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.signin'))
    
    user = conf[0] 
    type = conf[1]

    if not user :
        flash('Invalid/Expired Token', 'warning')
        return redirect(url_for('main.welcome'))

import socket
socket.getaddrinfo('localhost', 5000)
@auth.route('/test-mail/<email>')
def testmail(email):
    try:
        msg = Message("TEST MAIL Subject",sender='jameschristo962@gmail.com', recipients=['jameschristo962@gmail.com'])
        msg.body = "Mail body"
        msg.html = "<h2>Email Heading</h2>\n<p>Email Body</p>"
        print('')
        mail.send(msg)
        return 'successfully sent email'
    except:
        return 'failed-mail'



import smtplib
from socket import gaierror
@auth.route('/t-mail')
def sendm():
    """     port = 465  
    password = os.environ.get('EMAIL_PASSWORD')
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("my@gmail.com", password) """
    """     import urllib2

    #proxy_support = urllib2.ProxyHandler({"http":"http://61.233.25.166:80"})
    proxy_support = urllib2.ProxyHandler({"http":"http://localhost:5000"})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener) """

    import requests

    import urllib.request
    #htmlsource = urllib.request.FancyURLopener({"http":"http://127.0.0.1:5000"}).open(url).read().decode("utf-8")
    # url = urllib.request.FancyURLopener({"http":"http://127.0.0.1:5000"}).open('https://smtp.gmail.com').read().decode("utf-8")
    url = urllib.request.FancyURLopener({"http":"localhost:5000"}, timeout=0.1200).open('https://smtp.gmail.com').read().decode("utf-8")
    print(url.encoding)
    print(url.status_code)
    r = requests.get("https://smtp.gmail.com", proxies={"http": "localhost:5000"})
    #r = requests.get("https://smtp.gmail.com", proxies={"http": "127.0.0.1:5000"})
    # r = requests.get("https://www.google.com", 
    #                 proxies={"http": "localhost:5000"})
    #r = requests.get('http://www.thepage.com', proxies={"http":"http://myproxy:3129"})
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = 'socks5h://localhost:5000'
    session.proxies['https'] = 'socks5h://localhost:5003'
    r = session.get('https://google.com')

    thedata = r.content
    print(url)
    # the first step is always the same: import all necessary components:
    # import smtplib

    # now you can play with your code. Let’s define the SMTP server separately here:
    port = 5000 
    #smtp_server = "smtp.gmail.com" or r
    smtp_server = requests.get("https://smtp.gmail.com")
    login = "jameschristo962@gmail.com" # paste your login generated by Mailtrap
    password = "ckikkzvbbxdpgnub" # paste your password generated by Mailtrap
    # specify the sender’s and receiver’s email addresses
    sender = login
    receiver = "techa.tech99@gmail.com"
    # type your message: use two newlines (\n) to separate the subject from the message body, and use 'f' to  automatically insert variables in the text
    message = f"""\
    Subject: Hi Mailtrap
    To: {receiver}
    From: {sender}

    This is my first message with Python."""

    try:
        #send your message with credentials specified above
        with smtplib.SMTP(smtp_server, port) as server:
            server.login(login, password)
            server.sendmail(sender, receiver, message)
        # tell the script to report if your message was sent or which errors need to be fixed 
        print('Sent')
    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the server. Bad connection settings?')
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
        print('SMTP error occurred: ' + str(e))
