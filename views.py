from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for, Flask, make_response
from flask_login import login_required, current_user
from . import db
import json, random
import numpy as np
import pdfkit
from website.models import User, Semester, Subject, Module, Question, Subquestion, Template, Subquestiondetails, MCQ
import re
from nltk.stem import WordNetLemmatizer
import pickle

views = Blueprint('views', __name__)

def main(test_question):
    filename='finalized_model.sav'
    svm_classifier = pickle.load(open(filename, 'rb'))

    filename2='finalized_model2.sav'
    tf_idf = pickle.load(open(filename2, 'rb'))

    lemmatizer = WordNetLemmatizer()

    stopwords = ['a', 'the', 'is', 'an', 'of', 'at']
    review = re.sub('[^a-zA-Z]', ' ', test_question)
    review = review.lower()
    review = review.split()
    review = [lemmatizer.lemmatize(word)
            for word in review if not word in set(stopwords)]
    review = ' '.join(review)
    cleaned_test_question=review
    cleaned_test_question_tf = tf_idf.transform([cleaned_test_question])
    return svm_classifier.predict(cleaned_test_question_tf)[0]

@views.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    else:
        return render_template("landing.html", user=current_user)

@views.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)
    

@views.route('/semester', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        sem = request.form.get('sem')

        if len(sem) < 1:
            flash('Semester is should be of at least 1 character.', category='error')
        else:
            new_sem = Semester(sem=sem, user_id=current_user.id)
            db.session.add(new_sem)
            db.session.commit()
            flash("Semester added successfully!", category='success')
    return render_template("home.html", user=current_user)

@views.route('/delete-sem', methods=['POST'])
def delete_sem():
    sem = json.loads(request.data)
    semId = sem['semId']
    sem = Semester.query.get(semId)
    if sem:
        if sem.user_id == current_user.id:
            db.session.delete(sem)
            db.session.commit()
    return jsonify({})

@views.route('/update-sem', methods=['POST'])
def update_sem():
    newSem = json.loads(request.data)
    semId = newSem['semId']
    updatedField = newSem['updatedSem']
    sem = Semester.query.get(semId)
    if sem:
        if sem.user_id == current_user.id:
            sem.sem = updatedField
            db.session.commit()
    return jsonify({})

@views.route('/semester/<semId>', methods=['GET', 'POST'])
@login_required
def subjects(semId):
    if request.method == 'POST':
        subject = request.form.get('sub')
        if len(subject) < 2:
            flash('Subject name should be of at least 2 characters.', category="error")
        else:
            new_sub = Subject(subject_ame=subject, semester_id=semId)
            db.session.add(new_sub)
            db.session.commit()
            flash("Subject added successfully!", category='success')

    sem = Semester.query.filter_by(id=semId).first()
    return render_template("subjects.html", sem=sem, user=current_user)

@views.route('/delete-sub', methods=['POST'])
def delete_sub():
    sub = json.loads(request.data)
    subId = sub['subId']
    sub = Subject.query.get(subId)
    if sub:
            db.session.delete(sub)
            db.session.commit()
    return jsonify({})

@views.route('/update-sub', methods=['POST'])
def update_sub():
    newSub = json.loads(request.data)
    subId = newSub['subId']
    updatedField = newSub['updatedSub']
    sub = Subject.query.get(subId)
    if sub:
            sub.subject_ame = updatedField
            db.session.commit()
    return jsonify({})

@views.route('/semester/<semId>/<subId>', methods=['GET', 'POST'])
@login_required
def modules(semId, subId):
    if request.method == 'POST':
        module = request.form.get('mod')
        if len(module) < 1:
            flash('Module name should be of at least 1 character.', category="error")
        else:
            new_mod = Module(module_name=module, subject_id=subId)
            db.session.add(new_mod)
            db.session.commit()
            flash("Module added successfully!", category='success')

    sub = Subject.query.filter_by(id=subId).first()
    sem = Semester.query.filter_by(id=semId).first()
    return render_template("modules.html", user=current_user, sub=sub, sem=sem, semId=semId, subId=subId)

@views.route('/semester/<semId>/<subId>/mcq', methods=['GET', 'POST'])
@login_required
def add_mcq(semId, subId):
    if request.method == 'POST':
        mcq = request.form.get('mcq')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        if len(mcq) < 1:
            flash('MQuestion should be of at least 1 character.', category="error")
        else:
            new_mcq = MCQ(question=mcq, option1=option1, option2=option2, option3=option3, option4=option4, subject_id=subId)
            db.session.add(new_mcq)
            db.session.commit()
            flash("MCQ added successfully!", category='success')
    sub = Subject.query.filter_by(id=subId).first()
    return render_template("mcq.html", user=current_user, sub=sub, subId=subId, semId=semId)


@views.route('/delete-mcq', methods=['POST'])
def delete_mcq():
    mcq = json.loads(request.data)
    mcqId = mcq['mcqId']
    mcq = MCQ.query.get(mcqId)
    if mcq:
            db.session.delete(mcq)
            db.session.commit()
    return jsonify({})

@views.route('/delete-mod', methods=['POST'])
def delete_mod():
    mod = json.loads(request.data)
    modId = mod['modId']
    mod = Module.query.get(modId)
    if mod:
            db.session.delete(mod)
            db.session.commit()
    return jsonify({})

@views.route('/update-mod', methods=['POST'])
def update_mod():
    newMod = json.loads(request.data)
    modId = newMod['modId']
    updatedField = newMod['updatedMod']
    mod = Module.query.get(modId)
    if mod:
            mod.module_name = updatedField
            db.session.commit()
    return jsonify({})

@views.route('/semester/<semId>/<subId>/<modId>', methods=['GET', 'POST'])
@login_required
def questions(semId, subId, modId):
    if request.method == 'POST':
        question = request.form.get('question')
        predicted_class=main(question)
        print("Question:-",question)
        print("Class:-",predicted_class)
        if len(question) < 4:
            flash('Question should be of at least 4 characters.', category="error")
        else:
            new_ques = Question(question_content=question, module_id=modId, question_category=predicted_class)
            db.session.add(new_ques)
            db.session.commit()
            flash("Question added successfully!", category='success')

    mod = Module.query.filter_by(id=modId).first()
    sub = Subject.query.filter_by(id=subId).first()
    sem = Semester.query.filter_by(id=semId).first()
    return render_template("questions.html", user=current_user, mod=mod, sub=sub, sem=sem)

@views.route('/delete-question', methods=['POST'])
@login_required
def delete_question():
    ques = json.loads(request.data)
    quesId = ques['quesId']
    ques = Question.query.get(quesId)
    if ques:
            db.session.delete(ques)
            db.session.commit()
    return jsonify({})

@views.route('/update-question', methods=['POST'])
@login_required
def update_question():
    newQues = json.loads(request.data)
    quesId = newQues['quesId']
    updatedField = newQues['updatedQuestion']
    ques = Question.query.get(quesId)
    if ques:
            ques.question_content = updatedField
            db.session.commit()
    return jsonify({})

@views.route('/update-question-category', methods=['POST'])
@login_required
def update_question_category():
    newQues = json.loads(request.data)
    quesId = newQues['quesId']
    updatedField = newQues['updatedQuestionCategory']
    ques = Question.query.get(quesId)
    if ques:
            ques.question_category = updatedField
            db.session.commit()
    return jsonify({})

@views.route('/generate')
@login_required
def generate():
    id = current_user.id
    sems = Semester.query.filter_by(user_id=id)
    return render_template("select_sem.html", user=current_user, sems=sems)

@views.route('/generate/<semId>')
@login_required
def showSubs(semId):
    subs = Subject.query.filter_by(semester_id=semId)
    return render_template("select_sub.html", user=current_user, subs=subs, semId=semId)

@views.route('/generate/<semId>/<subId>')
@login_required
def displayTemplates(semId, subId):
    temps = Template.query.filter_by(user_id=current_user.id)
    return render_template("displayTemplates.html", user=current_user, temps=temps, semId=semId, subId=subId)
    # temps = Template.query.filter_by(user_id=current_user.id)
    # return render_template("displayTemplates.html", user=current_user, temps=temps, semId=semId, subId=subId)

@views.route('/delete-template', methods=['POST'])
@login_required
def delete_template():
    temp = json.loads(request.data)
    tempId = temp['tempId']
    temp = Template.query.get(tempId)
    if temp:
            db.session.delete(temp)
            db.session.commit()
    return jsonify({})

@views.route('/generate/<semId>/<subId>/create', methods=['GET', 'POST'])
@login_required
def createTemplate(semId, subId):
    if request.method == 'POST':
        user=current_user
        subject_code = request.form.get('subjectCode')
        duration = request.form.get('duration')
        instructions = request.form.get('instructions')
        name = request.form.get('templateName')
        mcqs = request.form.get('mcqs')
        total = int(request.form.get('totalQuestions'))
        compulsory = int(request.form.get('compulsoryQuestions'))
        optional = int(request.form.get('optionalQuestions'))
        marks = int(request.form.get('marks'))

        if len(name)<1:
            flash("Template name should be of at least 1 character", category="success")
        # elif ((compulsory+optional) != total):
        #     flash("Total questions are not equal to compulsory & optional questions", category="error")
        else:    
            new_template = Template(name=name, subject_code=subject_code, duration=duration, instructions=instructions, totalQ=total, compulsoryQ=compulsory, optionalQ=optional, marks=marks,user_id=user.id, mcqs=mcqs )
            db.session.add(new_template)
            db.session.commit()
            return redirect(url_for('views.addSubquestion', semId=semId, subId=subId, tempId=new_template.id))

    sub = Subject.query.filter_by(id=subId).first()
    if sub:
        return render_template("formatInfo.html", sub=sub, user=current_user)

@views.route('/generate/<semId>/<subId>/<tempId>', methods=['POST', 'GET'])
@login_required
def addSubquestion(semId, subId, tempId):
    if request.method == 'POST':
        temp = Template.query.filter_by(id=tempId).first()
        data = request.form
        question_dict = {}
        for key in data:
            new_question = Subquestion(question_number=key, subquestions=data[key], template_id=tempId)
            db.session.add(new_question)
            db.session.commit()
            question_dict[key] = new_question.id
        input = json.dumps(question_dict)
        return redirect(url_for('views.setTemplate', semId=semId, subId=subId, tempId=tempId, params=input, temp=temp))

    temp = Template.query.filter_by(id=tempId).first()
    compul = temp.compulsoryQ
    opt = temp.optionalQ
    if temp:
        return render_template("subQuestions.html", user=current_user, semId=semId, subId=subId, tempId=tempId, temp=temp, compul=compul, opt=opt)

@views.route('/generate/<semId>/<subId>/<tempId>/create/<params>', methods=['POST', 'GET'])
@login_required
def setTemplate(semId, subId, tempId, params):
    if request.method=='POST':
        dict = json.loads(params)
        modules = request.form.getlist('cMod')
        marks = request.form.getlist('cMarks')
        blooms = request.form.getlist('cCO')
        j=0
        for key in dict:
            ques = Subquestion.query.filter_by(id=dict[key]).first()
            subques = ques.subquestions
            for i in range(subques):
                new_subquestion = Subquestiondetails(module=modules[j], marks=marks[j], bloom=blooms[j], subquestion_of=dict[key])
                db.session.add(new_subquestion)
                db.session.commit()
                j=j+1
        return redirect(url_for('views.showTemplate', semId=semId, subId=subId, tempId=tempId))
        
    dict = json.loads(params)
    temp = Template.query.filter_by(id=tempId).first()
    sub = Subject.query.filter_by(id=subId).first()
    return render_template("setTemplate.html", user=current_user, subquestions=temp.subquestions, compulsory=temp.compulsoryQ, optional=temp.optionalQ, subject=sub, mcqs=temp.mcqs, marks=temp.marks)

@views.route('/generate/<semId>/<subId>/<tempId>/show', methods=['POST', 'GET'])
def showTemplate(semId, subId, tempId):
    if request.method == "POST":
        return redirect(url_for('views.questionPaper', semId=semId, subId=subId, tempId=tempId))
    temp = Template.query.filter_by(id=tempId).first()
    sub = Subject.query.filter_by(id=subId).first()
    return render_template("showTemplate.html", user=current_user, subquestions=temp.subquestions, compulsory=temp.compulsoryQ, optional=temp.optionalQ, subject=sub, mcqs=temp.mcqs)

@views.route('/generate/<semId>/<subId>/<tempId>/question_paper', methods=['POST', 'GET'])
def questionPaper(semId, subId, tempId):
    user = User.query.filter_by(id=current_user.id).first()
    sub = Subject.query.filter_by(id=subId).first()
    temp = Template.query.filter_by(id=tempId).first()
    sem = Semester.query.filter_by(id=semId).first()
    total_mcqs = temp.mcqs
    mcqs = sub.mcqs
    final_questions = []
    mcq_list = []
    if total_mcqs>0:
        for i in random.sample(sub.mcqs, total_mcqs):
            mcq_list.append(i)
        print(mcq_list)
    # for mcq in mcqs:
    #     print(mcq.question, mcq.option1, mcq.option2, mcq.option3, mcq.option4)
    
    for question in temp.subquestions:
        for subquestion in question.subques:
            module = Module.query.filter_by(module_name=subquestion.module).first()
            ques = Question.query.filter_by(module_id=module.id)
            list_of_ques = []
            for ques in module.questions:
                # MAIN IMPORTANT UPDATE
                if ques.question_category == subquestion.bloom:
                # if ques.question_category == 0:
                    list_of_ques.append(ques.question_content)
            ran = random.choice(list_of_ques)
            if ran not in final_questions:
                final_questions.append(ran)
            else:
                print("jhxb",list_of_ques)
                print("jhbax",final_questions)
                try:
                    main_list = np.setdiff1d(list_of_ques, final_questions)
                    print("123344",main_list)
                    final_questions.append(main_list[0])
                except:
                    final_questions=final_questions
    # return render_template("questionPaper.html", user=current_user, temp=temp, sem=sem, sub=sub, questions=temp.subquestions, questions_list=final_questions, subquestions=temp.subquestions, compulsory=temp.compulsoryQ, optional=temp.optionalQ, subject=sub, mcq_list=mcq_list, len=len(mcq_list))

    config = pdfkit.configuration(wkhtmltopdf='wkhtmltopdf.exe')
    print("CONFIG:-",config)
    rendered = render_template("questionPaper.html", user=current_user, temp=temp, sem=sem, sub=sub, questions=temp.subquestions, questions_list=final_questions, subquestions=temp.subquestions, compulsory=temp.compulsoryQ, optional=temp.optionalQ, subject=sub, mcq_list=mcq_list, len=len(mcq_list))
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Question Paper.pdf'
    return response