from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, ParentRelationship, db

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)

@views.route('/manage-child')
@login_required
def manage_child():
    if current_user.parent:
        if ParentRelationship.query.filter_by(parent_id=current_user.id).first() is None:
            return "You get 0 bitches"
        else:
            relationship = ParentRelationship.query.filter_by(parent_id=current_user.id).first()
            child_id = relationship.id
            return redirect(url_for('views.manage', child_id=child_id))

@views.route('/manage-child/<int:child_id>')
@login_required
def manage(child_id):
    if current_user.parent:
        children = [x for x in ParentRelationship.query.filter_by(parent_id=current_user.id)]
        children = [User.query.filter_by(id=x.child_id).first() for x in children]
        active_child = User.query.filter_by(id=child_id).first()
        return render_template('manage.html', user=current_user, children=children, active_child = active_child)
    else:
        return redirect('views.home')