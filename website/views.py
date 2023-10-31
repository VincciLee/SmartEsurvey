# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: views.py
# Description: Handle all routes and functions in the website
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import *
from . import db
import json
from werkzeug.utils import secure_filename
import os
from .functions import *
from .constants import *
from datetime import *
from dateutil.relativedelta import *
import pandas as pd
from sqlalchemy import desc, or_, and_
import random
import string

views = Blueprint('views', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'images')
DOWNLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'downloads')

characters = string.ascii_letters + string.digits

@views.route('/', methods=['GET','POST'])
@login_required
def home():
    surveys = Survey.query.order_by(desc(Survey.date_started)).filter_by(status='Opened')
    latest = []
    l_respondents = {}
    r_respondents = {}
    
    for s in surveys:
        if len(latest) < 3:
            date_started = date(int(s.date_started.split('-')[0]), int(s.date_started.split('-')[1]), int(s.date_started.split('-')[2]))
        
            if date_started <= date.today():
                latest.append(s)
        
        l_respondents[s.id] = Response.query.group_by(Response.date_submitted).filter_by(survey_id=s.id, status='Complete').count()
        
    recommends = get_recommendations(surveys, latest, current_user)
    for r in recommends:
        r_respondents[r.id] = Response.query.group_by(Response.date_submitted).filter_by(survey_id=r.id, status='Complete').count()
                
    if request.method == 'POST':
        search = request.form.get('search')
        
        return redirect(url_for('views.search_survey', search=search))

    return render_template("home.html", user=current_user, recommends=recommends, latest=latest, r_respondents=r_respondents, l_respondents=l_respondents)

@views.route('/search_survey/<search>', methods=['GET','POST'])
def search_survey(search):
    print('Searching')
    if request.method == 'POST':
        search = request.form.get('search')
    
    surveys = Survey.query.filter(
                or_(Survey.survey_code == search,
                    Survey.title.ilike('%{}%'.format(search))))
    
    respondents = {}
    for s in surveys:
        respondents[s.id] = Response.query.group_by(Response.date_submitted).filter_by(survey_id=s.id, status='Complete').count()
        
    return render_template("search_survey.html", user=current_user, surveys=surveys, respondents=respondents, search=search)
    
@views.route('/delete_survey', methods=['POST'])
def delete_survey():
    survey = json.loads(request.data)
    survey_id = survey['survey_id']
    db_survey = Survey.query.get(survey_id)
    if db_survey: 
        responses = Response.query.filter_by(survey_id=db_survey.id)
        for r in responses:
            db.session.delete(r)
           
        survey_details = Survey_Details.query.filter_by(survey_id=db_survey.id)
        for s in survey_details:
            db.session.delete(s)
         
        db.session.delete(db_survey)
        db.session.commit()
        
        flash('Survey deleted!', category='success')
            
    return jsonify({})

@views.route('/delete_response', methods=['POST'])
def delete_response():
    data = json.loads(request.data)
    db_response = Response.query.get(data['response_id'])
    
    print(db_response)
    
    if db_response: 
        responses = Response.query.filter_by(survey_id=db_response.survey_id, date_submitted=db_response.date_submitted, user_id=current_user.id)
        
        for r in responses:
            db.session.delete(r)
            
        db.session.commit()
      
    flash('Response deleted!', category='success')
                
    return jsonify({})

@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():      
    
    return render_template("profile.html", user=current_user)

@views.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        db_user = User.query.get(current_user.id)
        dob = request.form.get('dob')
        
        today = date.today()
        bday = date(int(dob.split('-')[0]), int(dob.split('-')[1]), int(dob.split('-')[2]))
        age = relativedelta(today, bday).years
        
        if age < 7:
            flash('User must be at least 7 years old!', category='error')
        else:
            db_user.username = request.form.get('username')
            db_user.gender = request.form.get('gender')
            db_user.dob = request.form.get('dob')
            db_user.occupation = request.form.get('occupation')
            db_user.institute = request.form.get('institute')
            db_user.field = request.form.get('field')
            
            upload_image = request.files['image']
            if upload_image:
                image_name = secure_filename(upload_image.filename)
                db_user.image = image_name
                
                image_path = os.path.join(UPLOAD_FOLDER, image_name)
                upload_image.save(image_path)
    
            db.session.commit()
            flash('Profile information updated!', category='success')
            return redirect(url_for('views.profile'))
            
    fields = get_field()
    occupations = get_occupation()
    
    return render_template("edit_profile.html", user=current_user, fields=fields, occupations=occupations)

@views.route('/create_survey', methods=['GET','POST'])
@login_required
def create_survey():
    fields = get_field()
    occupations = get_occupation()
    ages = get_age_group()
    today = date.today()
    closed_date = today + relativedelta(days=7)
    code = ''.join(random.choice(characters) for i in range(8))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        field_tag = request.form.get('field_tag')
        occupation_tag = request.form.get('occupation_tag')
        age_tag = request.form.get('age_tag')
        target = request.form.get('target')
        status = 'Opened'
        hidden = request.form.get('hidden')
        demographic = request.form.get('demographic')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        questions = request.form.getlist('questions[]')
        tips = request.form.getlist('tips[]')
        
        start_dt = date(int(start_date.split('-')[0]), int(start_date.split('-')[1]), int(start_date.split('-')[2]))
        close_dt = date(int(end_date.split('-')[0]), int(end_date.split('-')[1]), int(end_date.split('-')[2]))
        if today < start_dt:
            status = 'Pending'
        if today > close_dt:
            status = 'Closed'
            
        if start_dt > close_dt:
            flash('End Date must be later than Start Date!', category='error')
        else:
            new_survey = Survey(user_id=current_user.id, title=title, description=description, field_tag=field_tag, occupation_tag=occupation_tag, age_tag=age_tag, target=target, status=status, hidden=hidden, demographic=demographic, date_created=today, date_started=start_date, date_closed=end_date)
            
            db.session.add(new_survey)
            db.session.commit()
            
            db_survey = Survey.query.get(new_survey.id)
            db_survey.survey_code = 'su'+str(db_survey.id)+'_'+code
            db.session.commit()
            
            for i in range(0, len(questions)):
                survey_details = Survey_Details(survey_id=new_survey.id, sequence=i+1, question=questions[i], tips=tips[i])
                db.session.add(survey_details)
                db.session.commit()
                
            flash('Survey created successfully!', category='success')
            
            return redirect(url_for('views.home'))
    
    return render_template("create_survey.html", user=current_user, fields=fields, occupations=occupations, ages=ages, today=today, closed_date=closed_date)

@views.route('/do_survey/<survey_id>', methods=['GET','POST'])
@login_required
def do_survey(survey_id):
    survey = Survey.query.get(survey_id)
    details = Survey_Details.query.filter_by(survey_id=survey_id)
    author = User.query.get(survey.user_id)
    
    survey_dict = {}    
    survey_dict['intro'] = survey
    if survey.demographic == 'True':
        survey_dict['bioinfo'] = survey.demographic
    count = 0
    for d in details:
        survey_dict[d.sequence] = d
        count += 1
              
    if request.method == 'POST':
        button = request.form.get('button')
        answers = request.form.getlist('answers[]')
        sentiments = request.form.getlist('sentiments[]')
        status = 'Complete'
        date_submitted = datetime.now()
        null_found = False
        
        print(button)
        if button == 'Submit' and '' in answers:
            status = 'Draft'
            null_found = True
        elif button == 'Save':
            status = 'Draft'
        
        for i, ans in enumerate(answers):
            new_response = Response(user_id=current_user.id, survey_id=survey_id, question_id=details[i].id, answer=ans, real_sentiment=sentiments[i], status=status, date_submitted=date_submitted)
            db.session.add(new_response)
            
        db.session.commit()
        
        if null_found:
            flash('The response is saved as draft due to empty field submitted.', category='info')
            return redirect(url_for('views.participated_survey'))
        elif button == 'Save':
            flash('Your response is successfully saved as draft!', category='success')
            return redirect(url_for('views.participated_survey'))
        elif button == 'Submit':
            flash('Your response is successfully submitted!', category='success')
            return redirect(url_for('views.home'))
   
    return render_template("do_survey.html", user=current_user, author=author, survey=survey, details=details, survey_dict=survey_dict, ques_count=count)

@views.route('/edit_survey/<survey_id>', defaults={'status': 'All'}, methods=['GET','POST'])
@views.route('/edit_survey/<survey_id>/<status>', methods=['GET','POST'])
@login_required
def edit_survey(survey_id, status):
    today = date.today()
    fields = get_field()
    occupations = get_occupation()
    ages = get_age_group()
    survey = Survey.query.filter_by(id=survey_id).first()
    details = Survey_Details.query.filter_by(survey_id=survey_id)
    responses = Response.query.filter_by(question_id=details[0].id).count()
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        survey.title = request.form.get('title')
        survey.description = request.form.get('description')
        survey.field_tag = request.form.get('field_tag')
        survey.occupation_tag = request.form.get('occupation_tag')
        survey.age_tag = request.form.get('age_tag')
        survey.target = request.form.get('target')
        survey.status = 'Opened'
        survey.hidden = request.form.get('hidden')
        survey.demographic = request.form.get('demographic')
        survey.date_started = start_date
        survey.date_closed = request.form.get('end_date')
    
        start_dt = date(int(start_date.split('-')[0]), int(start_date.split('-')[1]), int(start_date.split('-')[2]))
        close_dt = date(int(end_date.split('-')[0]), int(end_date.split('-')[1]), int(end_date.split('-')[2]))
        if today < start_dt:
            survey.status = 'Pending'
        if today > close_dt:
            survey.status = 'Closed'
        
        if start_dt > close_dt:
            flash('End Date must be later than Start Date!', category='error')
        else:
            if responses == 0:    
                questions = request.form.getlist('questions[]')
                tips = request.form.getlist('tips[]')
                
                for d in details:
                    db.session.delete(d)
                
                for i in range(0, len(questions)):
                    survey_details = Survey_Details(survey_id=survey.id, sequence=i+1, question=questions[i], tips=tips[i])
                    db.session.add(survey_details)
            
            db.session.commit()
            flash('Survey updated!', category='success')
            return redirect(url_for('views.created_survey', status=status))
        
    return render_template("edit_survey.html", user=current_user, fields=fields, occupations=occupations, ages=ages, survey=survey, details=details, responses=responses)

@views.route('/export_csv/<survey_id>/<page>', methods=['GET','POST'])
@login_required
def export_csv(survey_id, page):
    survey = Survey.query.get(survey_id)
    details = Survey_Details.query.filter_by(survey_id=survey_id)
    responses = Response.query.group_by(Response.date_submitted, Response.user_id).filter_by(survey_id=survey_id)
    result = {}
    
    if survey.demographic == 'True':
        keys  = ['user_id', 'username', 'email', 'gender', 'dob', 'occupation', 'institute', 'field']
        result = dict(zip(keys, ([] for _ in keys)))
         
    result['date_submitted'] = []
     
    for r in responses:
        if survey.demographic == 'True':
            result['user_id'].append(r.user_id)
            
            user = User.query.get(r.user_id)
            result['username'].append(user.username)
            result['email'].append(user.email)
            result['gender'].append(user.gender)
            result['dob'].append(user.dob)
            result['occupation'].append(user.occupation)
            result['institute'].append(user.institute)
            result['field'].append(user.field)
            
        result['date_submitted'].append(r.date_submitted)
    
    model, vectorizer = load_model()          
    for d in details:
        ques = d.question
        sentiment = '{}_Predicted_Sentiment'.format(ques)
        result[ques] = []
        result[sentiment] = []
        
        for dt in result['date_submitted']:
            res = Response.query.filter_by(question_id=d.id, date_submitted=dt).first()
            result[ques].append(res.answer)
             
            answers = text_preprocessing([res.answer])
            review_vector = vectorizer.transform(answers)
            prediction = model.predict(review_vector)
            print(res.id, prediction)
            
            pred = ''
            if prediction[0] == 1:
                pred = 'Positive'
            elif prediction[0] == 0:
                pred = 'Neutral'
            elif prediction[0] == -1:
                pred = 'Negative'
            result[sentiment].append(pred)
            
    result_df = pd.DataFrame.from_dict(result) 
    survey_name = '_'.join([word for word in word_tokenize(survey.title)])
    today = str(datetime.now())
    today = today.replace(':', '-')
    today = today.replace(' ', '-')
    today = today.replace('.', '-')
    path = os.path.join(DOWNLOAD_FOLDER, '{}_{}.csv'.format(survey_name, today))
    result_df.to_csv(path, index=False)  
    
    flash('The result has been exported! Please check your download folder for the file.', category='success')
    
    return redirect(url_for('views.{}'.format(page), survey_id=survey_id))

@views.route('/view_result/<survey_id>', defaults={'keyword': None}, methods=['GET','POST'])
@views.route('/view_result/<survey_id>/<keyword>', methods=['GET','POST'])
@login_required
def view_result(survey_id, keyword):
    survey = Survey.query.get(survey_id)
    if survey.user_id != current_user.id and survey.hidden == 'True':
        flash('The result has hidden by the author!', category='error')
        
        return redirect(url_for('views.search_survey', search=keyword))
    else:
        details = Survey_Details.query.filter_by(survey_id=survey_id)
        responses = {}
        count = 0
        
        for d in details:
            responses[d.id] = Response.query.filter_by(question_id=d.id, status='Complete')
            
            if count == 0:
                count = Response.query.filter_by(question_id=d.id, status='Complete').count()
        
    return render_template("view_result.html", user=current_user, survey=survey, details=details, responses=responses, count=count)

@views.route('/view_result_summary/<survey_id>', methods=['GET','POST'])
@login_required
def view_result_summary(survey_id):
    survey = Survey.query.get(survey_id)
    details = Survey_Details.query.filter_by(survey_id=survey_id)
    responses = {}
    count = 0
    word_status = 'error'
    phrase_status = 'error'
    
    for d in details:
        responses[d.id] = Response.query.filter_by(question_id=d.id, status='Complete')
        
        if count == 0:
            count = Response.query.filter_by(question_id=d.id, status='Complete').count()
        
        image = 'word_cloud_s'+str(survey_id)+'_q'+str(d.id)+'.png'
        image2 = 'word_cloud_phrases_s'+str(survey_id)+'_q'+str(d.id)+'.png'
        
        image_path = os.path.join(UPLOAD_FOLDER, image)
        image_path2 = os.path.join(UPLOAD_FOLDER, image2)
        
        if os.path.exists(image_path):
            os.remove(image_path)
                
        if responses[d.id].count() > 0:
            cloud, message = word_cloud(responses[d.id], 'word')
            cloud2, message2 = word_cloud(responses[d.id], 'phrase')
            
            if message == 'success':
                cloud.to_file(image_path)
                word_status = 'success'
            if message2 == 'success':
                cloud2.to_file(image_path2)
                phrase_status = 'success'
            
    
    if responses[details[0].id].count() == 0:
        flash('There are no responses in this survey, therefore no word cloud can be generated.', category='info')
    elif responses[details[0].id].count() < 10:
        flash('There are too less responses at the moment, we recommend to see the summarization when there are at least 10 responses.', category='info')
      
    return render_template("view_result_summary.html", user=current_user, survey=survey, details=details, responses=responses, count=count, word_status=word_status, phrase_status=phrase_status)

@views.route('/view_result_sentiment/<survey_id>', methods=['GET','POST'])
@login_required
def view_result_sentiment(survey_id):
    model, vectorizer = load_model()
    survey = Survey.query.filter_by(id=survey_id).first()
    details = Survey_Details.query.filter_by(survey_id=survey_id)
    responses = {}
    sentiments = {}
    real_sentiments = {}
    count = 0
    
    for d in details:
        responses[d.id] = Response.query.filter_by(question_id=d.id, status='Complete')
        
        if count == 0:
            count = Response.query.filter_by(question_id=d.id, status='Complete').count()
        
        sentiments[d.id] = {'1': [], '0': [], '-1': []}
        real_sentiments[d.id] = {'1': [], '0': [], '-1': []}
        
        if responses[d.id].count() > 0:
            answers = []
            for r in responses[d.id]:
                answers.append(r.answer)
            
            answers = text_preprocessing(answers)
            review_vector = vectorizer.transform(answers)
            prediction = model.predict(review_vector)
            
            for i, p in enumerate(prediction):
                sentiments[d.id][str(p)].append(responses[d.id][i].answer)
                real_sentiments[d.id][str(p)].append(responses[d.id][i].real_sentiment)
              
    return render_template("view_result_sentiment.html", user=current_user, survey=survey, details=details, responses=responses, sentiments=sentiments, real_sentiments=real_sentiments, count=count)

@views.route('/view_result_demographic/<survey_id>', methods=['GET','POST'])
@login_required
def view_result_demographic(survey_id):
    survey = Survey.query.filter_by(id=survey_id).first()
    responses = Response.query.group_by(Response.date_submitted).filter_by(survey_id=survey_id)
    count = Response.query.group_by(Response.date_submitted).filter_by(survey_id=survey_id).count()
        
    survey_dict = {'field': {}, 'occupation': {}, 'age': {}, 'gender': {}}
    field_dict = {}
    occupation_dict = {}
    age_dict = {}
    gender_dict = {'Male': 0, 'Female': 0}
    for r in responses:
        respondent = User.query.get(r.user_id)
        
        try:
            field_dict[respondent.field] = field_dict[respondent.field] + 1
        except:
            field_dict[respondent.field] = 1
            
        try:
            occupation_dict[respondent.occupation] = occupation_dict[respondent.occupation] + 1
        except:
           occupation_dict[respondent.occupation] = 1
        
        age_group = calc_age_group(respondent.dob, 'Full')
        try:
            age_dict[age_group] = age_dict[age_group] + 1
        except:
            age_dict[age_group] = 1
            
        try:
            gender_dict[respondent.gender] = gender_dict[respondent.gender] + 1
        except:
           gender_dict[respondent.gender] = 1
    
    age_dict = dict(sorted(age_dict.items(), key=lambda x:x[1], reverse=True))
    field_dict = dict(sorted(field_dict.items(), key=lambda x:x[1], reverse=True))
    occupation_dict = dict(sorted(occupation_dict.items(), key=lambda x:x[1], reverse=True))
    
    survey_dict['field']['labels'] = json.dumps(list(field_dict.keys()))
    survey_dict['field']['values'] = json.dumps(list(field_dict.values()))
    survey_dict['occupation']['labels'] = json.dumps(list(occupation_dict.keys()))
    survey_dict['occupation']['values'] = json.dumps(list(occupation_dict.values()))
    survey_dict['age']['labels'] = json.dumps(list(age_dict.keys()))
    survey_dict['age']['values'] = json.dumps(list(age_dict.values()))
    survey_dict['gender']['labels'] = json.dumps(list(gender_dict.keys()))
    survey_dict['gender']['values'] = json.dumps(list(gender_dict.values()))
    
    return render_template("view_result_demographic.html", user=current_user, survey=survey, survey_dict=survey_dict, count=count)
 
@views.route('/participated_survey', defaults={'status': 'All'}, methods=['GET','POST'])
@views.route('/participated_survey/<status>', methods=['GET','POST'])
@login_required
def participated_survey(status):
    responses = None
    surveys = []
    
    if request.method == 'POST':
        status = request.form.get('status')
    
    try:
        if status == 'All':
            responses = Response.query.group_by(Response.date_submitted).order_by(desc(Response.date_submitted)).filter_by(user_id=current_user.id)
                
            for r in responses:
                surveys.append(Survey.query.get(r.survey_id))
        else:
            responses = Response.query.group_by(Response.date_submitted).order_by(desc(Response.date_submitted)).filter_by(user_id=current_user.id, status=status)
            
            for r in responses:
                surveys.append(Survey.query.get(r.survey_id))
    except:
        flash('You did not participate in any survey. Browse the homepage or search for a survey as a start!', category='info')
    finally:
        if len(surveys) == 0:
            flash('You did not participate in any survey. Browse the homepage or search for a survey as a start!', category='info')
       
    return render_template("participated_survey.html", user=current_user, surveys=surveys, responses=responses, status=status)

@views.route('/view_history/<response_id>', defaults={'page_status': 'All'}, methods=['GET','POST'])
@views.route('/view_history/<response_id>/<page_status>', methods=['GET','POST'])
@login_required
def view_history(response_id, page_status):
    response = Response.query.get(response_id)
    survey = Survey.query.get(response.survey_id)
    details = Survey_Details.query.filter_by(survey_id=survey.id)
    today = datetime.now()
    
    survey_dict = {}   
    responses = {}
     
    survey_dict['intro'] = survey
    if survey.demographic == 'True':
        survey_dict['bioinfo'] = survey.demographic
    count = 0
    for d in details:
        survey_dict[d.sequence] = d
        count += 1
        
        responses[d.sequence] = Response.query.filter_by(question_id=d.id, user_id=current_user.id, date_submitted=response.date_submitted).first()
    
    if request.method == 'POST':
        button = request.form.get('button')
        answers = request.form.getlist('answers[]')
        sentiments = request.form.getlist('sentiments[]')
        status = 'Complete'
        null_found = False
        
        if button == 'Submit' and '' in answers:
            status = 'Draft'
            null_found = True
        elif button == 'Save':
            status = 'Draft'
        
        for i, ans in enumerate(answers):
            responses[i+1].answer = ans
            responses[i+1].real_sentiment = sentiments[i]
            responses[i+1].status = status
            responses[i+1].date_submitted = today

        db.session.commit()
        
        if null_found:
            flash('The response is saved as draft due to empty field submitted.', category='info')
        elif button == 'Save':
            flash('Your response is successfully saved as draft!', category='success')
        elif button == 'Submit':
            flash('Your response is successfully submitted!', category='success')
    
        return redirect(url_for('views.participated_survey', status=page_status))
    
    return render_template("view_history.html", user=current_user, survey_dict=survey_dict, responses=responses, ques_count=count, status=page_status)

@views.route('/created_survey', defaults={'status': 'All'}, methods=['GET','POST'])
@views.route('/created_survey/<status>', methods=['GET','POST'])
@login_required
def created_survey(status):
    surveys = []
    respondents = {}
    
    if request.method == 'POST':
        status = request.form.get('status')

    try:    
        if status == 'All':
            surveys = Survey.query.order_by(desc(Survey.date_started)).filter_by(user_id=current_user.id)
        elif status == 'Opened' or status == 'Pending':
            surveys = Survey.query.order_by(desc(Survey.date_started)).filter_by(user_id=current_user.id, status=status)
        elif status == 'Closed':
            surveys = Survey.query.order_by(desc(Survey.date_closed)).filter_by(user_id=current_user.id, status=status)
        
        if surveys.count() > 0:
            for s in surveys:
                respondents[s.id] = Response.query.group_by(Response.date_submitted).filter_by(survey_id=s.id, status='Complete').count()
    except:
        flash('No survey found. Maybe you can create a new survey or wait for the existing survey to close.', category='info')
    
    return render_template("created_survey.html", user=current_user, surveys=surveys, status=status, respondents=respondents)

@views.route('/init_db', methods=['GET','POST'])
def init_db():
    # Delete all records in a table
    # db.session.query(User).delete()
    # db.session.query(Survey).delete()
    # db.session.query(Survey_Details).delete()
    # db.session.query(Response).delete()
    # db.session.commit()
    
    # delete specific survey
    # for i in range(11, 13):
    #     survey = Survey.query.get(i)  
    #     details = Survey_Details.query.filter_by(survey_id=i)
    #     responses = Response.query.filter_by(survey_id=i)
    #     for d in details:
    #         db.session.delete(d)  
    #     for r in responses:
    #         db.session.delete(r)  
    #     db.session.delete(survey)
    #     db.session.commit()
          
    # Initialize user account 
    rows = User.query.count()
    
    if rows == 0:
        username = ['user1', 'user2', 'user3', 'user4', 'user5']
        email = ['user1@mail.com', 'user2@mail.com', 'user3@mail.com', 'user4@mail.com', 'user5@mail.com']
        password = ['user1111', 'user2222', 'user3333', 'user4444', 'user5555']
        image = 'default.jpg'
        gender = ['Male', 'Female', 'Male', 'Female', 'Male']
        dob = ['2000-01-01', '1990-12-12', '2010-05-05', '1978-03-03', '1960-06-06']
        occupation = ['Student', 'Engineer', 'Doctor', 'Accountant', 'Teacher']
        institute = ['APU', 'Google', 'Hospital KL', 'Maybank', 'UM']
        field = ['Computer Science', 'Computer Science', 'Healthcare', 'Finance', 'Business']
        
        for i in range(len(username)):
            new_user = User(username=username[i], email=email[i], password=password[i], image=image, gender=gender[i], dob=dob[i], occupation=occupation[i], institute=institute[i], field=field[i])
            db.session.add(new_user)
        db.session.commit()
    
    # Initialize demo survey
    for i in range(0, 2):
        new_survey, responses = demo_surveys(i)
        db.session.add(new_survey)
        db.session.commit()
        
        questions = list(responses.keys())
        question_ids = []
        
        for i, key in enumerate(responses):
            new_details = Survey_Details(survey_id=new_survey.id, sequence=i+1, question=key, tips='')
            db.session.add(new_details)
            db.session.commit()
            
            question_ids.append(new_details.id)
        
        for i in range(0, len(responses[questions[0]][0])):
            user_id = random.randint(1, 5)
            date_submitted = datetime.now()
            
            try:
                for index, q_id in enumerate(question_ids):
                    print('-- responses --')
                    print(responses[questions[index]])
                    new_response = Response(user_id=user_id, survey_id=new_survey.id, question_id=q_id, answer=responses[questions[index]][0][i], real_sentiment=responses[questions[index]][1][i], status='Complete', date_submitted=date_submitted)
                    db.session.add(new_response)
                
                db.session.commit()
            except:
                continue
    
    for i in range(0, 8):    
        survey = randomize_survey(i)
        db.session.add(survey)
        db.session.commit()
        
        details = Survey_Details(survey_id=survey.id, sequence=1, question='What is your opinon about the survey topic?', tips='')
        db.session.add(details)
        details = Survey_Details(survey_id=survey.id, sequence=2, question='What do you think about the survey?', tips='What is your experience in doing the survey? Any improvements needed for the survey design?')
        db.session.add(details)
        db.session.commit()
       
    return redirect(url_for('auth.login'))
