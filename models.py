from . import db
from flask_login import UserMixin

# class Subquestion(db.Model):
#     id = db.Column(db.Integer, primary_key=True)

class Subquestiondetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(200))
    marks = db.Column(db.Integer)
    bloom = db.Column(db.Integer)
    subquestion_of = db.Column(db.Integer, db.ForeignKey('subquestion.id')) 

class Subquestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.Integer)
    subquestions = db.Column(db.Integer)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))
    subques = db.relationship('Subquestiondetails')


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    subject_code = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    instructions = db.Column(db.String(5000))
    mcqs = db.Column(db.Integer)
    totalQ = db.Column(db.Integer)
    compulsoryQ = db.Column(db.Integer)
    optionalQ = db.Column(db.Integer)
    marks = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subquestions = db.relationship('Subquestion')
    

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_content = db.Column(db.String(500))
    question_category = db.Column(db.Integer)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(200))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    questions = db.relationship('Question')

class MCQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500))
    option1 = db.Column(db.String(200))
    option2 = db.Column(db.String(200))
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_ame = db.Column(db.String(200))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    mods = db.relationship('Module')
    mcqs = db.relationship('MCQ')

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sem = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subs = db.relationship('Subject')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    full_name = db.Column(db.String(150))
    institution_name = db.Column(db.String(150))
    department = db.Column(db.String(300))
    designation = db.Column(db.String(150))
    sems = db.relationship('Semester')


