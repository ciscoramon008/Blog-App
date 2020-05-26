from flask import Flask
from flask_pymongo import PyMongo
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '7210c65e0a9630d80c20a76ae55ead60'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/flaskblog'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'primary'

from blogapp import routes