from urllib.parse import urlparse
from flask_login import login_user
from flask import redirect, url_for, flash, render_template
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm
from app import db
import logging

logger = logging.getLogger('main_logger')


def redirect_next_page(next_page):
    if not next_page or urlparse(next_page).netloc != '':
        next_page = url_for('auth.index')

    return redirect(next_page)


def valid_user_and_sign_in(form):
    user = User.query.filter_by(login=form.login.data).first()
    logger.info(f'Search user {form.login.data}')

    if user is None or not user.check_password(form.password.data):
        logger.info('Invalid login or password')
        return False

    is_user_sign_in = login_user(user, remember=form.remember_me.data)

    return is_user_sign_in


def main_login(current_user, request):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = LoginForm()

    if form.validate_on_submit():
        if valid_user_and_sign_in(form):
            return redirect_next_page(request.args.get('next'))
        else:
            flash('Invalid login or password')
            return redirect(url_for('auth.login'))

    return render_template('login.html', title='Sign In', form=form)


def save_user(user):
    db.session.add(user)
    db.session.commit()


def create_user(login, email, password):
    user = User(login=login, email=email)
    user.set_password(password)

    return user


def main_register(current_user):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = create_user(form.login.data, form.email.data, form.password.data)
        save_user(user)

        flash('Congratulations, you are now a registered user!')
        logger.info('User registered')

        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register', form=form)
