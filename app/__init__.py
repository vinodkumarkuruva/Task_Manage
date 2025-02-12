from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

# Initialize extensions

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir+'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Change this in production

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production for HTTPS
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'  # Path where the access cookie is valid
app.config['JWT_REFRESH_COOKIE_PATH'] = '/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Enable CSRF protection for cookies

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


from app.views import app as main_app
app.register_blueprint(main_app)
