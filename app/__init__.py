import os,sys
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flasgger import Swagger

app = Flask(__name__)

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": 'ExpEYES-17 Online',
    "specs": [
        {
            "version": "0.0.1",
            "title": "ExpEYES17-Online API",
            "description": "This is the draft version of ExpEYES-Online API",
            "endpoint": "v1_spec",
            "route": "/v1/spec",
        }
    ]
}

Swagger(app)
CORS(app,supports_credentials=True)

app.secret_key = 'yet another secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)

from app import views

