from pyexpat.errors import messages

from flask import make_response, jsonify, Blueprint, request
from flask_restful import Resource
from app import api, db
from app.todo.models import User, Tasks
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.todo.serde import UserSchema, TaskSchema
from app.todo.controllers.validation import FieldValidations

todo_blueprint = Blueprint("todo", __name__)


class HealthCheck(Resource):
    def get(self):
        try:
            return make_response(jsonify({"message": "THis is health check api"}))
        except Exception as error:
            return make_response(jsonify({"message": str(error)}))


class UserRegister(Resource):
    """This is to create users"""

    def post(self):
        try:
            email = request.json.get("email", "NA")
            password = request.json.get("password", "NA")
            email_validation = FieldValidations()
            email_validation_key = email_validation.email_validation(email)
            if email_validation_key:
                user_object = User()
                user_object.email = email
                user_object.password = password
                db.session.add(user_object)
                db.session.commit()
                return make_response(jsonify({"message": "Successful Created Account"}))
            else:
                raise Exception("Invalid Email id")

        except Exception as error:
            return make_response(jsonify({"message": f"str{error}"}))


class Login(Resource):
    """Login Api"""

    def post(self):
        try:
            email = request.json.get("email")
            password = request.json.get("password")
            email_validation = FieldValidations()

            if email_validation.email_validation(email):
                if email_validation.find_password(password, email):
                    access_token = create_access_token(identity=email)
                    refresh_token = create_refresh_token(identity=email)
                    return make_response(jsonify({"acces-token": access_token, "refresh-token": refresh_token}))
                else:
                    return make_response(jsonify({"message": "You have Entred Incorrect Password!"}))
            else:
                return make_response(jsonify({"message": "Please Check your mail its and incorrect!"}))
        except Exception as error:
            return make_response(jsonify({"message": f"str{error}"}))


class ListTask(Resource):
    """List all the task of a users"""

    @jwt_required()
    def get(self, user_id):
        try:
            email = get_jwt_identity()
            validation = FieldValidations()
            print(f"JWT Identity: {email}")

            # jwt check
            if not validation.find_email(email):
                return jsonify({"message": "Invalid Email"}), 401

            # users check
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Fetch all tasks for the user
            tasks = user.tasks.all()

            # Serialize the tasks using TaskSchema
            try:
                task_schema = TaskSchema(many=True)  # many=True for a list of tasks
                serialized_tasks = task_schema.dump(tasks)
            except ValidationError as err:
                return {"error": "Serialization error", "details": err.messages}, 500

            return {"tasks": serialized_tasks}, 200

        except Exception as error:
            print(f"Error: {str(error)}")
            return jsonify({'error': str(error)}), 500


class CreateTask(Resource):
    @jwt_required()
    def post(self, user_id):
        validation = FieldValidations()
        email = get_jwt_identity()
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

            # serde model
            try:
                task_schema = TaskSchema()
                serialized_task = task_schema.dump(new_task)
            except ValidationError as err:
                return {"error": "Serialization error", "details": err.messages}, 500

            return {
                'message': 'Task updated successfully',
                'task': serialized_task
            }, 201
        else:
            return jsonify({"message": "Invalid Token"})


class UpdateTask(Resource):

    @jwt_required()
    def put(self, task_id):
        validation = FieldValidations()
        email = get_jwt_identity()

        if validation.find_email(email):
            task = Tasks.query.get(task_id)
            if not task:
                return {'error': 'Task not found'}, 404

            # get the inputs fields
            data = request.get_json()

            # validation for fields
            title = data.get('title')
            if title is not None:
                task.title = title

            description = data.get('description')
            if description is not None:
                task.description = description

            is_completed = data.get('is_completed')
            if is_completed is not None:
                if isinstance(is_completed, bool):
                    task.is_completed = is_completed
                else:
                    return {'error': 'Invalid value for is_completed. Must be a boolean.'}, 400

            due_date = data.get('due_date')
            if due_date:
                try:
                    from datetime import datetime
                    task.due_date = datetime.fromisoformat(due_date)
                except ValueError:
                    return {'error': 'Invalid date format. Use ISO 8601.'}, 400

            # update the updated_at
            task.updated_at = datetime.now()

            db.session.commit()

            # serde model
            try:
                task_schema = TaskSchema()
                serialized_task = task_schema.dump(task)
            except ValidationError as err:
                return {"error": "Serialization error", "details": err.messages}, 500

            return {
                'message': 'Task updated successfully',
                'task': serialized_task
            }, 200
        else:
            return jsonify({"message": "Invalid Token"}), 403


class DeleteTask(Resource):
    @jwt_required()
    def delete(self, user_id, task_id):
        try:
            email = get_jwt_identity()
            validation = FieldValidations()
            print(f"JWT Identity: {email}")
            # jwt check
            if not validation.find_email(email):
                return jsonify({"message": "Invalid Email"}), 401

            # users check
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # get task
            task = Tasks.query.filter_by(id=task_id, user_id=user_id).first()
            if not task:
                return {"error": "Task not found or does not belong to the user"}, 404

            db.session.delete(task)
            db.session.commit()

            return {"message": "Task deleted successfully"}, 200

        except Exception as error:
            return jsonify({"message": str(error)})


api.add_resource(HealthCheck, "/v1/api/health/")
api.add_resource(UserRegister, "/v1/api/register/")
api.add_resource(Login, "/v1/api/login/")
api.add_resource(ListTask, "/v1/api/<int:user_id>/list")
api.add_resource(CreateTask, "/v1/api/<int:user_id>/create")
api.add_resource(UpdateTask, "/v1/api/<int:task_id>/update")
api.add_resource(DeleteTask, "/v1/api/<int:user_id>/<int:task_id>/delete")
