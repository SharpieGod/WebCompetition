from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, ParentRelationship
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    email = ''
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user, email=email)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    email = ''
    first_name = ''
    last_name = ''

    if request.method == 'POST':
        email = request.form.get('email').lower()
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        parent = request.form.get('parent') is not None

        user = User.query.filter_by(email=email, parent=parent).first()
        if user:
            flash('Email is already in use.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters long.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='sha256'), parent=parent)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign up.html', user=current_user, email=email, first_name=first_name, last_name=last_name)


@auth.route('/add-child', methods=['GET', 'POST'])
@login_required
def add_child():
    child_email = ''
    child_first_name = ''
    child_last_name = ''

    if current_user.parent is True:
        if request.method == 'POST':
            child_email = request.form.get('child_email').lower()
            child_first_name = request.form.get('childFirstName')
            child_last_name = request.form.get('childLastName')
            child_password = request.form.get('child_password')
            parent_password = request.form.get('parent_password')

            users = User.query.filter_by(
                email=child_email, first_name=child_first_name, last_name=child_last_name, parent=0)
            user = [x for x in users if check_password_hash(
                x.password, child_password)]
            child_user = None

            if user:
                child_user = user[0]

            if child_user is not None:
                if check_password_hash(child_user.password, child_password):
                    if check_password_hash(current_user.password, parent_password):
                        if ParentRelationship.query.filter_by(parent_id=current_user.id, child_id=child_user.id).first() is None:
                            flash(
                                f'Added {child_first_name} to children list successfully!', category='success')
                            relationship = ParentRelationship(
                                parent_id=current_user.id, child_id=child_user.id)
                            db.session.add(relationship)
                            db.session.commit()
                            return redirect(url_for('views.home'))
                        else:
                            flash('Parent relationship already exists',
                                  category='error')
                    else:
                        flash('Incorrect parent password.', category='error')
                else:
                    flash('Incorrect child password.', category='error')
            else:
                flash(
                    'Child email address or first name or last name are incorrect.', category='error')

        return render_template('add-child.html', user=current_user, first_name=child_first_name, last_name=child_last_name, email=child_email)
    else:
        return redirect(url_for('views.home'))
