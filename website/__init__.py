# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: __init__.py
# Description: A script to initialize the website
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import *
from dateutil.relativedelta import *

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    # initialize Flask
    app = Flask(__name__)
    
    # secure cookies on the website
    app.config['SECRET_KEY'] = 'f1fj23hj123ghj'
    
    # import route
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # import db tables
    from .models import User, Survey, Response
    
    with app.app_context():
        create_database(app)
        refresh_survey_status(Survey, Response)
    
    login_manager = LoginManager( )
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # .get always look for primary key
    
    return app
    
def create_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.app = app
    db.init_app(app)
    db.create_all()
    print('Created Database!')
    
def refresh_survey_status(Survey, Response):
    today = date.today()
    surveys = Survey.query.all()
    
    if len(surveys) > 0:
        print('Updating survey status!')
        for s in surveys:
            start_date = s.date_started
            close_date = s.date_closed
            start_dt = date(int(start_date.split('-')[0]), int(start_date.split('-')[1]), int(start_date.split('-')[2]))
            close_dt = date(int(close_date.split('-')[0]), int(close_date.split('-')[1]), int(close_date.split('-')[2]))
            
            # update status based on date condition
            if today > close_dt:
                s.status = 'Closed'
            elif s.status == 'Pending' and start_dt <= today:
                s.status = 'Opened'
            elif start_dt > today:
                s.status = 'Pending'
            elif start_dt <= today and today <= close_dt:
                s.status = 'Opened'
        
        db.session.commit()
      
    