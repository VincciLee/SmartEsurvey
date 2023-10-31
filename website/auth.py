# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: auth.py
# Description: Handle the signup, login and logout function
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import *
from werkzeug.utils import secure_filename
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .constants import get_field, get_occupation
from datetime import *
from dateutil.relativedelta import *
import os

auth = Blueprint('auth', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'images')

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                
                return redirect(url_for('views.home'))
            else:
                flash('The email or password is not correct, please try again', category='error')
        else:
            flash('The email or password is not correct, please try again', category='error')
            
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    today = date.today()
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        image = 'default.jpg'
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        occupation = request.form.get('occupation')
        institute = request.form.get('institute')
        field = request.form.get('field')
        
        upload_image = request.files['image']
        if upload_image:
            image = secure_filename(upload_image.filename)
            
        bday = date(int(dob.split('-')[0]), int(dob.split('-')[1]), int(dob.split('-')[2]))
        age = relativedelta(today, bday).years
        
        user = User.query.filter_by(email=email).first()
        
        if gender == None:
            flash('Please select a gender!', category='error')
        elif occupation == None:   
            flash('Please select an occupation!', category='error')
        elif field == None:    
            flash('Please select a field!', category='error')
        elif age < 7:
            flash('User must be at least 7 years old!', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters!', category='error')
        elif user:
            flash('The email address has been registered!', category='error')
        else:
            image_path = os.path.join(UPLOAD_FOLDER, image)
            if upload_image:
                upload_image.save(image_path)
            
            new_user = User(username=username, email=email, password=password1, image=image, gender=gender, dob=dob, occupation=occupation, institute=institute, field=field)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Sign up successfully! Welcome to SmartEsurvey!', category='success')
            
            return redirect(url_for('views.home'))

    fields = get_field()
    occupations = get_occupation()
    
    return render_template("sign_up.html", user=current_user, fields=fields, occupations=occupations, today=str(today))