from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        # Check if user is locked out
        if user.login_locked:
            lockout_time = user.lockout_time + timedelta(minutes=60)
            if lockout_time > datetime.utcnow():
                flash('Account is locked due to too many failed login attempts. Please try again later.')
                return redirect(url_for('auth.login'))

            # Unlock user after lockout time has expired
            user.unlock()

        # Check password and lockout user if necessary
        if not user.check_password(form.password.data):
            user.add_login_attempt()
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        # Login user and redirect
        login_user(user, remember=form.remember_me.data)
        user.login_attempts = 0
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
@login_required
def reset_password_request():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.user', username=current_user.username))
        else:
            flash('Invalid old password.')
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)