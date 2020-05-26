from flask import render_template, url_for, flash, redirect, session, g
from blogapp import app, mongo, bcrypt, login_manager
from blogapp.forms import RegistrationForm, LoginForm
from flask_login import login_user

posts = [
    {
        'author': 'Cisco Ramon',
        'title': 'Post 1',
        'content': 'First Post Content',
        'date_posted': 'April 20, 2017'
    },
    {
        'author': 'Barry Allen',
        'title': 'Post 2',
        'content': 'Second Post Content',
        'date_posted': 'March 2, 2020'
    },
]

user_collection = mongo.db.users

class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    u = user_collection.find_one({'username': username})
    if not u:
        return None
    return User(username=u['username'])

@app.route('/')
def home():
    return render_template('home.html', posts = posts)

@app.route('/about')
def about():
    return render_template('about.html', title = 'About')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # condition for image file

        user_collection.insert_one({
            'username': form.username.data,
            'password': hashed_pw,
            'email': form.email.data
        })

        flash(f'Your Account Has Been Createad! You Can Login Now', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        person = user_collection.find_one({'email': login.email.data})
        if person and bcrypt.check_password_hash(person['password'], login.password.data):
            user_obj = User(person['username'])
            print(user_obj)
            login_user(user_obj, login.remember.data)
            flash('Welcome to BlogApp', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email or password again.', 'danger')
    return render_template('login.html', title = 'Login', form = login)

# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('home'))

# @app.route('/profile')
# def profile():
#     print('\n', g.user, '\n')
#     if not g.user:
#         return redirect(url_for('home'))
#     else:
#         return '<h1>WELCOME TO THE SECRET PAGE YOU!</h1>'