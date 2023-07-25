from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum


class GradeEnum(Enum):
    E = "Extending"
    A = "Applying"
    D = "Developing"
    B = "Beginning"
    I = "Insufficient Evidence"


class ParentRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    child_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class GradeRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Enum(GradeEnum))
    subject = db.Column(db.String(150))
    grade_comment = db.Column(db.String(350))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    parent = db.Column(db.Boolean)
