from flask import render_template, url_for, redirect, session, current_app, abort, flash
from flask_login import login_required, current_user
from .. import db
from . import main
from ..models import Role, User, Permission
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from ..email import send_mail
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None:
			session['known'] = False
			user = User(username=form.username.data)
			db.session.add(user)
			db.session.commit()
			send_mail(current_app.config['FLASK_ADMIN'], 'New user', 'new_user',
				user=user)
		else:
			session['known'] = True
		session['username'] = form.username.data
		form.username.data = ''
		return redirect(url_for('.index'))
	return render_template('index.html', form=form, known=session.get('known', False),
		username=session.get('username'))

@main.route('/user/<username>')
@login_required
def user_profile(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	return render_template('user-profile.html', user=user)

@main.route('/user/<username>/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
	if User.query.filter_by(username=username).first() != current_user:
		abort(404)
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash('Your profile has been updated.')
		return redirect(url_for('.user_profile', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('auth/register.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('The profile has been updated.')
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('auth/register.html', form=form)