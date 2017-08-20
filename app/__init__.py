import os,sys
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app,supports_credentials=True)

app.secret_key = 'yet another secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)

from app import views

