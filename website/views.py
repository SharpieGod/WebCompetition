from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, ParentRelationship, db, GradeRelationship, Grade, GradeEnum

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
            relationship = ParentRelationship.query.filter_by(
                parent_id=current_user.id).first()
            child_id = relationship.id
            return redirect(url_for('views.manage', child_id=child_id))


@views.route('/grades')
@login_required
def grades():
    if not current_user.parent:
        grade_relationships = GradeRelationship.query.filter_by(
            child_id=current_user.id)

        grades = []

        for grade_relationship in grade_relationships:
            grades.append(Grade.query.filter_by(
                id=grade_relationship.grade_id).first())

        return render_template('grades.html', user=current_user, grades=grades)
    else:
        return redirect(url_for('views.home'))


@views.route('/add-grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    if request.method == 'POST':
        grade = request.form.get('grade')
        subject = request.form.get('subject')
        grade_comment = request.form.get('grade_comment')

        if grade != 'None':
            if subject != 'None':
                if grade_comment != '':
                    new_grade = Grade(grade=GradeEnum(
                        grade), subject=subject, grade_comment=grade_comment)
                    db.session.add(new_grade)
                    db.session.commit()
                    new_grade_relationship = GradeRelationship(
                        child_id=current_user.id, grade_id=new_grade.id)

                    db.session.add(new_grade_relationship)
                    db.session.commit()
                    flash('Added grade successfully.', category='success')
                    return redirect(url_for('views.grades'))
                else:
                    flash('You must include a grade comment.', category='error')
            else:
                flash('You must include a subject.', category='error')
        else:
            flash('You must include a grade.', category='error')

    if not current_user.parent:
        grade_options = ['Extending', 'Applying',
                         'Developing', 'Beginning', 'Insufficient Evidence']
        grades = [GradeEnum.E, GradeEnum.A,
                  GradeEnum.D, GradeEnum.B, GradeEnum.I]
        subject_options = ["Math", "Science",    "English",    "Social Studies",    "History",    "Geography",    "World History",    "US History",    "European History",    "Asian Studies",    "Latin American Studies",    "African Studies",    "Physical Education",    "Health",    "Art",    "Music",    "Drama",    "Theater",    "Film Studies",    "Media Studies",    "Journalism",    "Creative Writing",    "Computer Science",    "Programming",    "Web Development",
                           "Data Science",    "Statistics",    "Business",    "Economics",    "Marketing",    "Accounting",    "Finance",    "Foreign Languages",    "Spanish",    "French",    "German",    "Italian",    "Chinese",    "Japanese",    "Korean",    "Arabic",    "Hebrew",    "Russian",    "Portuguese",    "Biology",    "Chemistry",    "Physics",    "Environmental Science",    "Psychology",    "Sociology",    "Anthropology",    "Philosophy",    "Religious Studies"]
        return render_template('add-grade.html', user=current_user, grade_options=grade_options, subject_options=subject_options, grades=grades)
    else:
        return redirect(url_for('views.home'))


@views.route('/manage-child/<int:child_id>')
@login_required
def manage(child_id):
    if current_user.parent:
        children = [x for x in ParentRelationship.query.filter_by(
            parent_id=current_user.id)]
        children = [User.query.filter_by(
            id=x.child_id).first() for x in children]
        active_child = User.query.filter_by(id=child_id).first()
        grade_relationships = GradeRelationship.query.filter_by(
            child_id=active_child.id)
        grades = [Grade.query.filter_by(id=x.grade_id).first()
                  for x in grade_relationships]

        return render_template('manage.html', user=current_user, children=children, active_child=active_child, grades=grades)
    else:
        return redirect('views.home')
