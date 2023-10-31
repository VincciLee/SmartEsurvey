# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: constants.py
# Description: Functions that return a list of predefined values
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

import pandas as pd
import random
import string
from datetime import *
from dateutil.relativedelta import *
from .models import *

def get_occupation():
    occupation = ['Doctor', 'Engineer', 'Accountant', 'Student', 'Teacher']
    return occupation

def get_field():
    field = ['Healthcare', 'Computer Science', 'Finance', 'Business']
    return field

def get_age_group():
    age = {'0-11': 'Below 12 years old', '12-15': '12 to 15 years old', '16-20': '16 to 20 years old', '21-30': '21 to 30 years old', '31-45': '31 to 45 years old', '46-60': '46 to 60 years old', '61-150': 'Above 60 years old'}
    return age

def demo_surveys(num):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for i in range(8))
    
    user_id = 1
    survey_code = 'su000_'+code
    title = ['Residential Community Survey', 'Election Survey']
    description = ['This survey is for demo purpose of opinion about residential community. The dataset is provided by a student from APD3F2211CSIS.','This survey is for demo purpose of opinion about election. ']
    field_tag = ['Any', 'Business']
    occupation_tag = ['Student', 'Any']
    age_tag = ['21-30', '31-45']
    target = 50
    status = 'Opened'
    hidden = ['True', 'False']
    demographic = ['True', 'False']
    date_created = '2023-07-01'
    date_started = '2023-07-01'
    date_closed = '2023-09-21'
    
    survey = Survey(user_id=user_id, survey_code=survey_code, title=title[num], description=description[num], field_tag=field_tag[num], occupation_tag=occupation_tag[num], age_tag=age_tag[num], target=target, status=status, hidden=hidden[num], demographic=demographic[num], date_created=date_created, date_started=date_started, date_closed=date_closed)
    
    datasets = ['demo_dataset.csv', 'demo_dataset2.csv']
    questions = [['How do you communicate with the committee members of your residential community and why?', 'Why do you participate/not participate in the activities organised by your residential community?','When visiting a residential community that requires registration at the guard house, how do you feel about it and why do you feel that way?'], ['What is your opinion about the election?']]
    
    data = pd.read_csv('website\\datasets\\{}'.format(datasets[num]))
    responses = {}
    
    for q in questions[num]:
        # q = question, s = sentiment where the value is the column name
        s = '{}_Sentiment'.format(q)
        result = data.loc[:, [q, s]]
        result = result.dropna()
        
        responses[q] = []
        responses[q].append(list(result[q]))
        responses[q].append(list(result[s]))
    
    return survey, responses

def randomize_survey(num):
    titles = ['Hobby Survey', 'University Survey', 'Mobile Apps Survey', 'Cafeteria Survey', 'Library Survey', 'Travel Experience Survey', 'Family Survey', 'Savings Habit Survey', 'Working Experience Survey', 'Interview Survey']
    fields = get_field()
    occupations = get_occupation()
    ages = get_age_group()
    age_keys = list(ages.keys())
    tf = ['True', 'False']
    
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for i in range(8))
    
    user_id = random.randint(1,5)
    survey_code = 'su000_'+code
    title = titles[num]
    field_tag = fields[random.randint(0,3)]
    occupation_tag = occupations[random.randint(0,4)]
    age_tag = age_keys[random.randint(1,5)]
    target = random.randint(10,50)
    status = 'Opened'
    hidden = tf[num%2]
    demographic = tf[num%2]
    date_created = '2023-06-01'
    date_started = date(2023, 7, 1) + relativedelta(days=random.randint(0,7)) - relativedelta(days=random.randint(0,7))
    date_closed = date(2023, 9, 15) + relativedelta(days=random.randint(0,15)) - relativedelta(days=random.randint(0,15))
    description = 'This {} is for demo purpose for the proposed project. The survey is opened for people from {} age group, {} occupation, and {} study field.'.format(title, age_tag, occupation_tag, field_tag)
    
    survey = Survey(user_id=user_id, survey_code=survey_code, title=title, description=description, field_tag=field_tag, occupation_tag=occupation_tag, age_tag=age_tag, target=target, status=status, hidden=hidden, demographic=demographic, date_created=date_created, date_started=date_started, date_closed=date_closed)
    
    return survey