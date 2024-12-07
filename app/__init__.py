import os
from datetime import timedelta
from flask import Flask, request,jsonify,make_response,Blueprint
from flask_restful import Resource,Api
from dotenv import load_dotenv
# import secrets
from flask_jwt_extended import jwt_manager,JWTManager
from flask_sqlalchemy import SQLAlchemy



load_dotenv()
app = Flask(__name__)
api = Api(app)
app.config["JWT_SECRET_KEY"] = "amit"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)

hostname = 'localhost'
database = 'todo'
username = 'postgres'
pwd = 'amit'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{username}:{pwd}@localhost:5432/{database}"
db =  SQLAlchemy(app)
