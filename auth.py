from flask import Blueprint, redirect, render_template, request, flash, url_for
from .models import User, Semester, Subject, Module, Question, Template, Subquestion, Subquestiondetails, MCQ
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
                return redirect(url_for('auth.login'))
        else:
            flash('This email does not exist. Please sign up!', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('fullName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        institution_name = request.form.get('institutionName')
        department = request.form.get('department')
        designation = request.form.get('designation')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email is already taken! Please try another one.', category='error')
        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(full_name) < 2:
            flash('Full Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash("Passwords don't match", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif len(institution_name) < 3:
            flash('Institution Name must be greater than 2 characters.', category='error')
        elif len(department) < 2:
            flash('Department must be greater than 1 character.', category='error')
        elif len(designation) < 5:
            flash('Designation must be at least 5 characters.', category='error')
        
        else:
            try: 
                new_user = User(email=email, full_name=full_name, institution_name=institution_name, department=department, designation=designation, password=generate_password_hash(password1, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='succes')
                return redirect(url_for('views.dashboard'))
            except Exception as e:
                    flash(e, category='error')
        
    return render_template("sign_up.html",user=current_user)

@auth.route('/database', methods=['GET', 'POST'])
def database():
    return render_template("database.html", users=User.query.all(), sems=Semester.query.all(), subs=Subject.query.all(), mods=Module.query.all(), ques=Question.query.all(), temps=Template.query.all(), subques=Subquestion.query.all(), subqueinfo=Subquestiondetails.query.all(), mcqs=MCQ.query.all())

