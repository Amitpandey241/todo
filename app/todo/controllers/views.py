from pyexpat.errors import messages

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

            if email_validation.email_validation(email):
                if email_validation.find_password(password,email):
                    access_token = create_access_token(identity=email)
                    refresh_token = create_refresh_token(identity=email)
                    return make_response(jsonify({"acces-token": access_token, "refresh-token": refresh_token}))
                else:
                    return make_response(jsonify({"message": "You have Entred Incorrect Password!"}))
            else:
                return make_response(jsonify({"message": "Please Check your mail its and incorrect!"}))
        except Exception as error:
            return make_response(jsonify({"message": f"str{error}"}))

class Todo(Resource):
    @jwt_required()
    def get(self, user_id):
        try:
            email = get_jwt_identity()
            validation = FieldValidations()
            print(f"JWT Identity: {email}")
            # jwt check
            if not validation.find_email(email):
                return jsonify({"message": "Invalid Email"}), 401

            #users check
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            tasks = user.tasks.all()
            tasks_list = [
                {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'is_completed': task.is_completed,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                }
                for task in tasks
            ]

            return {"tasks": tasks_list}, 200

        except Exception as error:
            print(f"Error: {str(error)}")
            return jsonify({'error': str(error)}), 500

    @jwt_required()
    def post(self,user_id):
        validation = FieldValidations()
        email=get_jwt_identity()
        if validation.find_email(email):
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404

            data = request.get_json()

            title = data.get('title')
            if not title:
                return {'error': 'Task title is required'}, 400

            description = data.get('description', '')
            is_completed = data.get('is_completed', False)
            due_date = data.get('due_date')

            due_date_obj = None
            if due_date:
                try:
                    from datetime import datetime
                    due_date_obj = datetime.fromisoformat(due_date)
                except ValueError:
                    return {'error': 'Invalid date format. Use ISO 8601.'}, 400

            new_task = Tasks(
                title=title,
                description=description,
                is_completed=is_completed,
                due_date=due_date_obj,
                user=user,
            )

            db.session.add(new_task)
            db.session.commit()

            return {
                'message': 'Task created successfully',
                'task': {
                    'id': new_task.id,
                    'title': new_task.title,
                    'description': new_task.description,
                    'is_completed': new_task.is_completed,
                    'due_date': new_task.due_date.isoformat() if new_task.due_date else None,
                    'created_at': new_task.created_at.isoformat(),
                    'updated_at': new_task.updated_at.isoformat() if new_task.updated_at else None,
                }
            }, 201
        else:
            return jsonify({"message": "Invalid Token"})
    @jwt_required()
    def delete(self,user_id,task_id):
        try:
            email = get_jwt_identity()
            validation = FieldValidations()
            print(f"JWT Identity: {email}")
            #jwt check
            if not validation.find_email(email):
                return jsonify({"message": "Invalid Email"}), 401

            #users check
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            #get task
            task = Tasks.query.filter_by(id=task_id, user_id=user_id).first()
            if not task:
                return {"error": "Task not found or does not belong to the user"}, 404

            db.session.delete(task)
            db.session.commit()

            return {"message": "Task deleted successfully"}, 200

        except Exception as error:
            return jsonify({"message":str(error)})

api.add_resource(HealthCheck, "/v1/api/health/")
api.add_resource(UserRegister,"/v1/api/register/")
api.add_resource(Login,"/v1/api/login/")
api.add_resource(Todo,"/v1/api/<int:user_id>/task")