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
        return redirect(url_for('main.index'))
    form = SignupForm()
    if form.validate_on_submit():
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # user = User(username=form.username.data, email=form.email.data, password=hashed_password,  ip =ip_adrs.user_ip())
        user = User(username=form.username.data, email=form.email.data,  ip =ip_adrs.user_ip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        email.verify_email(user) if user else flash('Undefined User.', 'info')
        flash('Your Account Has Been Created! You Are Now Able To Log In', 'success')
        return redirect(url_for('auth.signin'))
    return render_template('auth/signup.html', title='Sign-up', form=form)


@auth.route("/signin", methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
        # if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Re-hash using scrypt if the password was hashed with bcrypt
            if user.password.startswith("$2b$"):  # bcrypt hash prefix
                user.set_password(form.password.data)
                db.session.commit()
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
    current_user.online = False
    logout_user()
    db.session.commit()
    return redirect(url_for('main.index'))

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
        return redirect(url_for('main.index'))
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

#->for both verify/reset/forgot etc tokens
@auth.route("/confirm/<token>/<email>", methods=['GET', 'POST'])
def confirm(token: str, email: str):

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Ensure token_type is present
    if not token or not email:
        print('<token & email> not found', 'warning')
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'warning')
        return redirect(url_for('main.index'))
    
    user = User.check_token(user, token)
    
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.index'))

    # Ensure token_type is present
    if not hasattr(user, 'token_type'):
        flash('Token type not found', 'warning')
        print('Token type not found', 'warning')
        return redirect(url_for('main.index'))
    
    if user.token_type == 'confirm_email':
        if user.verified:
            flash(f'You have already verified your email address, {user.username}.', 'success')
        else:
            user.verified = True
            db.session.commit()
            flash(f'Email address confirmed for {user.username}.', 'success')
        return redirect(url_for('auth.signin'))

    elif user.token_type == 'reset_password':
        form = ResetForm()
        if form.validate_on_submit():
            user.password = user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.signin'))
        
        return render_template('reset_password.html', form=form)
    
    return redirect(url_for('main.index'))

@auth.route("/confirm/<token>", methods=['GET', 'POST'])
def confirm1(token: str):

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.check_token(token)
    print(user.token_type)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        print('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.index'))

    # token_type = token_data["token_type"]
    
    if user.token_type == 'confirm_email':
        if user.verified:
            flash(f'You have already verified your email address, {user.username}.', 'success')
        else:
            user.verified = True
            db.session.commit()
            flash(f'Email address confirmed for {user.username}.', 'success')
        return redirect(url_for('auth.signin'))

    elif user.token_type == 'reset_password':
        form = ResetForm()
        if form.validate_on_submit():
            # hashed_password = user.set_password(form.password.data)
            user.password =  user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.signin'))
        
        return render_template('auth/reset.html', user=user, form=form)
    
    return redirect(url_for('main.index'))

@auth.route('/notify')
@login_required
def notify():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(Notification.created > since).order_by(Notification.created.asc())
    return jsonify([{ 'name': n.name, 'data': n.get_data(), 'timestamp': n.created } for n in notifications])

