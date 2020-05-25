from flask import Flask, render_template, url_for, flash, redirect
# from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from forms import RegistrationForm, LoginForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '7210c65e0a9630d80c20a76ae55ead60'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/flaskblog'
mongo = PyMongo(app)



# class User(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     username = db.Column(db.String(20), unique = True, nullable = False)
#     email = db.Column(db.String(120), unique = True, nullable = False)
#     image = db.Column(db.String(120), nullable = False, default = 'default.jpeg')
#     password = db.Column(db.String(60), nullablue = False)
#     posts = db.relationship('Post', backref = 'author', lazy = True)

#     def __repr__(self):
#         return f"User ('{self.username}', '{self.email}', '{self.image}')"

# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     title = db.Column(db.String(100), nullable = False)
#     date_poster = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
#     content = db.Column(db.Text, nullable = False)
#     user_id = db.Columnt(db.Integer, db.ForeignKey('user.id'), nullable = False)

#     def __repr__(self):
#         return f"Post ('{self.username}', '{self.title}', '{self.date_posted}')"


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

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts = posts)

@app.route('/about')
def about():
    return render_template('about.html', title = 'About')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        if login.email.data == 'admin@blog.com' and login.password.data == 'password':
            flash(f'You have successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Something went wrong!', 'danger')
    return render_template('login.html', title = 'Login', form = login)

@app.route('/user')
def user():
    user_collection = mongo.db.users
    user_collection.insert_one({'name': 'Kaustav'})
    return '<h1>ADDED AN USER</h1>'

if __name__ == '__main__':
    app.run(debug=True)
