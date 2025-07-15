from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo, bcrypt
from app.models import User
from flask import current_app
import os

main = Blueprint('main', __name__)



@main.route('/')
def welcome():
    return render_template('welcome.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            return redirect(url_for('main.register'))

        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert into DB
        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw
        })

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user_data = mongo.db.users.find_one({"email": email})

        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/map')
@login_required
def map_view():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('map.html', api_key=api_key)

@main.route('/calorie', methods=['GET', 'POST'])
@login_required
def calorie_calculator():
    result = None
    if request.method == 'POST':
        gender = request.form['gender']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        activity = float(request.form['activity'])

        # Mifflin-St Jeor RMR formula
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        maintenance_calories = bmr * activity
        result = round(maintenance_calories)

    return render_template('calories.html', result=result)

@main.route('/about')
def about():
    return render_template('about.html')

