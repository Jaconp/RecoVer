from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User
from forms import LoginForm, RegistrationForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Debug log for login route
    print("Login route accessed!")
    
    if current_user.is_authenticated:
        print(f"User already authenticated as {current_user.username}, redirecting to index")
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        print(f"Form submitted with email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            print(f"User {user.username} successfully authenticated")
            login_user(user, remember=form.remember.data)
            print(f"User logged in: {current_user.is_authenticated}")
            
            next_page = request.args.get('next')
            if next_page:
                print(f"Redirecting to next page: {next_page}")
            else:
                print("Redirecting to index page")
                
            flash(f'Welcome back, {user.username}! You have successfully logged in.', 'success')
            return redirect(next_page if next_page else url_for('index'))
        else:
            print("Authentication failed")
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form, title='Login')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Debug log for register route
    print("Register route accessed!")
    
    if current_user.is_authenticated:
        print(f"User already authenticated as {current_user.username}, redirecting to index")
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        print(f"Registration form submitted: {form.username.data} / {form.email.data}")
        
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            print(f"Email {form.email.data} already registered")
            flash('Email already registered. Please use a different email or login.', 'danger')
            return render_template('register.html', form=form, title='Register')
        
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            print(f"Username {form.username.data} already taken")
            flash('Username already taken. Please choose a different username.', 'danger')
            return render_template('register.html', form=form, title='Register')
        
        # Create new user
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        
        # Make the first user an admin
        if User.query.count() == 0:
            print("Setting first user as admin")
            user.is_admin = True
        
        print(f"Adding user to database: {user.username}")
        db.session.add(user)
        db.session.commit()
        print(f"User created with ID: {user.id}")
        
        # Log the user in immediately after successful registration
        print("Logging in new user")
        login_user(user)
        print(f"Authentication status after login: {current_user.is_authenticated}")
        
        flash(f'Welcome, {user.username}! Your account has been created successfully. You are now logged in.', 'success')
        print("Redirecting to index")
        return redirect(url_for('index'))
    elif form.errors:
        print(f"Form validation errors: {form.errors}")
    
    return render_template('register.html', form=form, title='Register')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')
