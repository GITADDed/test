from app.auth import bp
from flask import render_template, redirect, url_for, request
from flask_login import current_user, logout_user, login_required
from app.auth.func import main_login, main_register


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('base.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    return main_login(current_user, request)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    return main_register(current_user)
