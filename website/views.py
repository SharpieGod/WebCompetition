from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, ParentRelationship, db, GradeRelationship, Grade, GradeEnum
from werkzeug.datastructures import MultiDict
import json

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
            return render_template('no-children.html', user=current_user)
        else:
            relationship = ParentRelationship.query.filter_by(
                parent_id=current_user.id).first()
            child_id = relationship.child_id
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

    grade_options = ['Extending', 'Applying',
                     'Developing', 'Beginning', 'Insufficient Evidence']
    grades = [GradeEnum.E, GradeEnum.A,
              GradeEnum.D, GradeEnum.B, GradeEnum.I]
    subject_options = ["Math", "Science",    "English",    "Social Studies",    "History",    "Geography",    "World History",    "US History",    "European History",    "Asian Studies",    "Latin American Studies",    "African Studies",    "Physical Education",    "Health",    "Art",    "Music",    "Drama",    "Theater",    "Film Studies",    "Media Studies",    "Journalism",    "Creative Writing",    "Computer Science",    "Programming",    "Web Development",
                       "Data Science",    "Statistics",    "Business",    "Economics",    "Marketing",    "Accounting",    "Finance",    "Foreign Languages",    "Spanish",    "French",    "German",    "Italian",    "Chinese",    "Japanese",    "Korean",    "Arabic",    "Hebrew",    "Russian",    "Portuguese",    "Biology",    "Chemistry",    "Physics",    "Environmental Science",    "Psychology",    "Sociology",    "Anthropology",    "Philosophy",    "Religious Studies"]

    if request.method == 'POST':
        grade = request.form.get('grade')
        subject = request.form.get('subject')
        grade_comment = request.form.get('grade_comment')

        if grade in grade_options or subject in subject_options:
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
                        flash('You must include a grade comment.',
                              category='error')
                else:
                    flash('You must include a subject.', category='error')
            else:
                flash('You must include a grade.', category='error')
        else:
            flash('Don\'t do that please.', category='error')

    if not current_user.parent:
        subject_options = sorted(subject_options)

        return render_template('add-grade.html', user=current_user, grade_options=grade_options, subject_options=subject_options, grades=grades)
    else:
        return redirect(url_for('views.home'))


@views.route('/manage-child/<int:child_id>', methods=['GET', 'POST'])
@login_required
def manage(child_id):
    grade_options = ['Extending', 'Applying',
                     'Developing', 'Beginning', 'Insufficient Evidence']

    subject_options = ["Math", "Science",    "English",    "Social Studies",    "History",    "Geography",    "World History",    "US History",    "European History",    "Asian Studies",    "Latin American Studies",    "African Studies",    "Physical Education",    "Health",    "Art",    "Music",    "Drama",    "Theater",    "Film Studies",    "Media Studies",    "Journalism",    "Creative Writing",    "Computer Science",    "Programming",    "Web Development",
                       "Data Science",    "Statistics",    "Business",    "Economics",    "Marketing",    "Accounting",    "Finance",    "Foreign Languages",    "Spanish",    "French",    "German",    "Italian",    "Chinese",    "Japanese",    "Korean",    "Arabic",    "Hebrew",    "Russian",    "Portuguese",    "Biology",    "Chemistry",    "Physics",    "Environmental Science",    "Psychology",    "Sociology",    "Anthropology",    "Philosophy",    "Religious Studies"]

    args = MultiDict()
    subject_filter = request.args.get('subjectFilter')
    grade_filter = request.args.get('gradeFilter')

    if request.method == 'POST':
        subject_filter = request.form.get('subject_filter')
        grade_filter = request.form.get('grade_filter')

        if subject_filter:
            if subject_filter in subject_options:
                args['subjectFilter'] = subject_filter

        if grade_filter:
            if grade_filter in grade_options:
                args['gradeFilter'] = grade_filter

        return redirect(url_for('views.manage', **args.to_dict(flat=False), child_id=child_id))

    if current_user.parent:
        children = [x for x in ParentRelationship.query.filter_by(
            parent_id=current_user.id)]
        children = [User.query.filter_by(
            id=x.child_id).first() for x in children]

        if not children:
            return redirect(url_for('views.manage_child'))

        active_child = User.query.filter_by(id=child_id).first()
        grade_relationships = GradeRelationship.query.filter_by(
            child_id=active_child.id)
        grades = [Grade.query.filter_by(id=x.grade_id).first()
                  for x in grade_relationships]

        subject_options = sorted(subject_options)

        if subject_filter:
            args["subjectFilter"] = subject_filter
            grades = [x for x in grades if x.subject == subject_filter]

        if grade_filter:
            args["gradeFilter"] = grade_filter
            grades = [x for x in grades if x.grade.value == grade_filter]

        grades = enumerate(grades)
        return render_template('manage.html', user=current_user, children=children, active_child=active_child, grades=grades, subjects=subject_options, grade_options=grade_options, subject_filter=subject_filter, grade_filter=grade_filter)
    else:
        return redirect('views.home')


@views.route('/edit-grade/<int:grade_id>', methods=['GET', 'POST'])
def edit_grade(grade_id):
    if not current_user.parent:
        return redirect(url_for('views.home'))

    grade_relationship = GradeRelationship.query.filter_by(
        grade_id=grade_id).first()

    if grade_relationship is None:
        return redirect(url_for('views.manage_child'))

    grade = Grade.query.filter_by(id=grade_id).first()

    grade_options = ['Extending', 'Applying',
                     'Developing', 'Beginning', 'Insufficient Evidence']

    subject_options = ["Math", "Science",    "English",    "Social Studies",    "History",    "Geography",    "World History",    "US History",    "European History",    "Asian Studies",    "Latin American Studies",    "African Studies",    "Physical Education",    "Health",    "Art",    "Music",    "Drama",    "Theater",    "Film Studies",    "Media Studies",    "Journalism",    "Creative Writing",    "Computer Science",    "Programming",    "Web Development",
                       "Data Science",    "Statistics",    "Business",    "Economics",    "Marketing",    "Accounting",    "Finance",    "Foreign Languages",    "Spanish",    "French",    "German",    "Italian",    "Chinese",    "Japanese",    "Korean",    "Arabic",    "Hebrew",    "Russian",    "Portuguese",    "Biology",    "Chemistry",    "Physics",    "Environmental Science",    "Psychology",    "Sociology",    "Anthropology",    "Philosophy",    "Religious Studies"]

    subject_options = sorted(subject_options)

    if request.method == 'POST':
        request_grade = request.form.get('grade')
        subject = request.form.get('subject')
        grade_comment = request.form.get('grade_comment')

        if request_grade not in grade_options or subject not in subject_options:
            flash('Don\'t do that', category='error')
        elif grade_comment == "":
            flash('Grade comment cannot be empty', category='error')
        else:
            grade.grade = GradeEnum(request_grade)
            grade.subject = subject
            grade.grade_comment = grade_comment

            db.session.commit()
            return redirect(url_for('views.manage_child'))

    return render_template('edit-grade.html', user=current_user, grade=grade, subject_options=subject_options, grade_options=grade_options)


@views.route('/delete-grade', methods=['POST'])
def delete_grade():
    grade_data = json.loads(request.data)
    gradeId = grade_data['gradeId']
    grade = Grade.query.get(gradeId)
    grade_relationship = GradeRelationship.query.filter_by(
        grade_id=grade.id).first()
    parent_relationship = ParentRelationship.query.filter_by(
        child_id=grade_relationship.child_id).first()

    if grade:
        if current_user.id == parent_relationship.parent_id:
            db.session.delete(grade)
            db.session.delete(grade_relationship)
            db.session.commit()

    return jsonify({})
