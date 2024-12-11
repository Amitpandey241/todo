from flask import make_response, jsonify, Blueprint, request
from flask_restful import Resource
from app import api,db
from app.todo.models import User, Tasks
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from app.todo.controllers.validation import FieldValidations

todo_blueprint = Blueprint("todo", __name__)

class HealthCheck(Resource):
    def get(self):
        try:
            return make_response(jsonify({"message": "THis is health check api"}))
        except Exception as error:
            return make_response(jsonify({"message": str(error)}))


class UserRegister(Resource):
    def post(self):
        try:
            email = request.json.get("email","NA")
            password = request.json.get("password", "NA")
            email_validation = FieldValidations()
            email_validation_key = email_validation.email_validation(email)
            if email_validation_key:
                user_object  = User()
                user_object.email = email
                user_object.password = password
                db.session.add(user_object)
                db.session.commit()
                return make_response(jsonify({"message":"Successful Created Account"}))
            else:
                raise Exception("Invalid Email id")

        except Exception as error:
            return make_response(jsonify({"message": f"str{error}"}))

class Login(Resource):
    def post(self):
        try:
            email = request.json.get("email")
            password = request.json.get("password")
            email_validation = FieldValidations()
            email_validation_key = email_validation.email_validation(email)
            if email_validation_key:
                if 

# class Todo(Resource):
#     def post(self):
#         try:
#         except Exception as error:


api.add_resource(HealthCheck, "/v1/api/health/")
api.add_resource(UserRegister,"/v1/api/register/")
