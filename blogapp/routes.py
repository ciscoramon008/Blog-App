import secrets
import os
from datetime import datetime
from bson.objectid import ObjectId
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from blogapp import app, mongo, bcrypt, login_manager
from blogapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required

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
    
    def __eq__(self, other):
        return self.username == other.username and self.email == other.email and self.image == other.image

@login_manager.user_loader
def load_user(username):
    u = user_collection.find_one({'username': username})
    if not u:
        return None
    return User(u['username'], u['email'], u['image'])

@app.route('/')
def home():
    posts = mongo.db.posts.find()

    passing_posts = []

    for post in posts:
        post_author = user_collection.find_one({'_id': post['author']})
        post['author'] = post_author
        passing_posts.append(post)

    return render_template('home.html', posts = passing_posts)

    # posts.

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
        user_collection.insert_one({
            'username': form.username.data,
            'password': hashed_pw,
            'email': form.email.data,
            'image': 'default.jpeg',
            'posts': []
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

        # a = {
        #     'username': usr
        # }

        # posts = dict(mongo.db.posts.find({'author': a}))
        # print(posts)

        # for doc in posts:
        #     print(doc)

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
    form = PostForm()
    if form.validate_on_submit():
        post_collection = mongo.db.posts
        now_user = user_collection.find_one({'username': current_user.username})
        print(now_user)
        created_post = post_collection.insert_one({
            'title': form.title.data,
            'content': form.content.data,
            'author': now_user['_id'],
            'date_posted': datetime.utcnow().strftime('%Y-%m-%d')
        })

        user_collection.update_one({'username': current_user.username}, {
            '$push': {
                'posts':  created_post.inserted_id
            }
        })


        flash('Your post has been successfully created.', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title = 'New Post', form = form, legend = 'New Post')


@app.route('/post/<post_id>', methods = ['GET', 'POST'])
@login_required
def post(post_id):
    posts_collection = mongo.db.posts
    now_post = posts_collection.find_one({'_id': ObjectId(post_id)})
    now_post_author = user_collection.find_one({'_id': ObjectId(now_post['author'])})
    current_post_author = User(now_post_author['username'], now_post_author['email'], now_post_author['image'])
    now_post['author'] = now_post_author
    return render_template('post.html', title = now_post['title'], post = now_post, current_post_author = current_post_author)

@app.route('/post/<post_id>/update', methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    posts_collection = mongo.db.posts
    now_post = posts_collection.find_one({'_id': ObjectId(post_id)})
    now_post_author = user_collection.find_one({'_id': ObjectId(now_post['author'])})
    current_post_author = User(now_post_author['username'], now_post_author['email'], now_post_author['image'])
    now_post['author'] = now_post_author

    if current_post_author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        posts_collection.find_and_modify({'_id': ObjectId(post_id)}, {
            '$set': {
                'title': form.title.data,
                'content': form.content.data
            }
        })
        flash('You post has been updated.', 'success')
        return redirect(url_for('post', post_id = post_id))
    elif request.method == 'GET':
        form.title.data = now_post['title']
        form.content.data = now_post['content']
    return render_template('new_post.html', title = now_post['title'], form = form, legend = 'Update Post')


@app.route('/post/<post_id>/delete', methods = ['POST'])
@login_required
def delete_post(post_id):
    posts_collection = mongo.db.posts
    post_to_delete = posts_collection.find_one({'_id': ObjectId(post_id)})

    now_post_author = user_collection.find_one({'_id': ObjectId(post_to_delete['author'])})
    current_post_author = User(now_post_author['username'], now_post_author['email'], now_post_author['image'])

    if current_post_author != current_user:
        abort(403)
    
    posts_collection.find_one_and_delete({'_id': ObjectId(post_to_delete['_id'])})

    flash('Your post has been successfully deleted.', 'success')
    return redirect(url_for('home'))