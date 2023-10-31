# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: models.py
# Description: A script to initialize the database tables and attributes
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))    
    email = db.Column(db.String(150), unique=True)  
    password = db.Column(db.String(50))    
    image = db.Column(db.String(150))
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(15))     
    occupation = db.Column(db.String(150))
    institute = db.Column(db.String(150))
    field = db.Column(db.String(150))
   
class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    survey_code = db.Column(db.String(20))   
    title = db.Column(db.String(100))         
    description = db.Column(db.String(1000))   
    field_tag = db.Column(db.String(150))     
    occupation_tag = db.Column(db.String(150))    
    age_tag = db.Column(db.String(150))       
    target = db.Column(db.Integer)        
    status = db.Column(db.String(10))        
    demographic = db.Column(db.String(10))      
    hidden = db.Column(db.String(10))
    date_created = db.Column(db.String(30))  
    date_started = db.Column(db.String(30))  
    date_closed = db.Column(db.String(30))   
    
class Survey_Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    sequence = db.Column(db.Integer)
    question = db.Column(db.String(150))  
    tips = db.Column(db.String(1000))      
    
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('survey__details.id'))
    answer = db.Column(db.String(300))    
    real_sentiment = db.Column(db.String(10))      
    status = db.Column(db.String(10)) 
    date_submitted = db.Column(db.String(30))    
    