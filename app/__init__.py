import os
from datetime import timedelta
from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
api = Api(app)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = "amit"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:amit@localhost:5432/todo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models to associate them with `db`
from app.todo.models import User, Tasks

# Import and register blueprints
from app.todo.controllers.views import todo_blueprint
app.register_blueprint(todo_blueprint)

# Export `app` and `db` for external use
__all__ = ["app", "db"]
