from flask import redirect, render_template, url_for, flash, request
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.login import current_user

from . import auth
from .forms import *
from .. import db
from ..models import User
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid email or passwrod.')
	return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form =RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, 
				username=form.username.data,
				password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm Your Accout',
					'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to you.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
	else:
		flash('Then confirmation link is invalid or has expired.')
	return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
				and request.endpoint[:5] != 'auth.':
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


@auth.route('/resend_confiremation')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, 'Confirm Your Accout',
			'auth/email/confirm',user=current_user, token=token)
	flash('A new confirmation email has been resend to you.')
	return redirect(url_for('main.index'))
	

@auth.route('/password-change', methods=['GET', 'POST'])
@login_required
def password_change():
	form = PasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash('Your password has been changed.')
			return redirect(url_for('main.index'))
		flash('Old password not match.')
	return render_template('auth/password_change.html', form=form)


@auth.route('/password-reset', methods=['GET', 'POST'])
def password_reset_request():
	form = Email()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_email(user.email, 'Reset Your Password',
					'auth/email/confirm_reset_password', user=user, 
					token=token, next=request.args.get('next'))
		flash('A confirm email has been send to you.')
		return redirect(url_for('auth.login'))
	return render_template('auth/password_reset.html', form=form)


@auth.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash('Your password has been reseted.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/password_reset.html', form=form)










