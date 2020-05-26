import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from blogapp import app, mongo, bcrypt, login_manager
from blogapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required

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
    def __init__(self, username, email, image):
        self.username = username
        self.image = image
        self.email = email

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
    return User(u['username'], u['email'], u['image'])

@app.route('/')
def home():
    return render_template('home.html', posts = posts)

@app.route('/about')
def about():
    return render_template('about.html', title = 'About')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # condition for image file

        user_collection.insert_one({
            'username': form.username.data,
            'password': hashed_pw,
            'email': form.email.data,
            'image': 'default.jpeg'
        })

        flash(f'Your Account Has Been Createad! You Can Login Now', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login = LoginForm()
    if login.validate_on_submit():
        person = user_collection.find_one({'email': login.email.data})
        if person and bcrypt.check_password_hash(person['password'], login.password.data):
            user_obj = User(person['username'], person['email'], person['image'])
            login_user(user_obj, login.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            flash('Welcome to BlogApp', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email or password again.', 'danger')
    return render_template('login.html', title = 'Login', form = login)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_pic(form_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_pic)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.pic.data:
            current_user.image = save_pic(form.pic.data)
        usr = current_user.username
        current_user.username = form.username.data
        current_user.email = form.email.data
        user_collection.find_and_modify({'username': usr} ,{
            '$set':{
                'username': form.username.data,
                'email': form.email.data,
                'image': current_user.image
            }
        })
        flash('Your account has been updated', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/{current_user.image}')
    return render_template('profile.html', title = 'Profile', image = image_file, form = form)

@app.route('/post/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    return render_template('new_post.html')