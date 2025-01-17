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
    """
        Handles user registration by creating a new user account.

        Args:
        email (str): The email address of the user obtained from the request body.
        password (str): The password of the user obtained from the request body.

        Returns:
        Response: JSON response with a success message if the user account is created successfully.
                If the email validation fails or any exception occurs, a JSON response with an error message is returned.
    """

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
    """
        Handles user login and provides access and refresh tokens upon successful authentication.

        Args:
            email (str): The email address provided by the user in the request body.
            password (str): The password provided by the user in the request body.

        Returns:
            Response:
                - JSON response with `access-token` and `refresh-token` if login is successful.
                - JSON response with an error message if the email validation or password validation fails.
    """

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
    """
        Lists all tasks associated with a specific user.

        Args:
            user_id (int): The ID of the user whose tasks need to be fetched.

        Returns:
            Response:
                - 200: A JSON object containing a list of tasks serialized using `TaskSchema`.
                - 401: If the JWT token is invalid or the email is not found.
                - 404: If the user with the specified `user_id` does not exist.
                - 500: If there is an internal server error or a serialization issue.
    """

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
    """
        Creates a new task for a specific user.

        Args:
            user_id (int): The ID of the user for whom the task is being created.

        Returns:
            Response:
                - 201: A JSON object containing a success message and the details of the created task.
                - 400: If the task title is missing or the due date format is invalid.
                - 404: If the user with the specified `user_id` is not found.
                - 500: If there is a serialization error or other internal server issue.
                - 401: If the token is invalid.
    """


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
    """
        Updates the details of a specific task.

        Args:
            task_id (int): The ID of the task to be updated.

        Returns:
            Response:
                - 200: A JSON object containing a success message and the updated task details.
                - 400: If any input field (e.g., `is_completed` or `due_date`) contains invalid data.
                - 404: If the task with the specified `task_id` is not found.
                - 403: If the token is invalid.
                - 500: If there is a serialization error or other internal server issue.
    """
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
    """
        Deletes a specific task for a given user.

        Args:
            user_id (int): The ID of the user to whom the task belongs.
            task_id (int): The ID of the task to be deleted.

        Returns:
            Response:
                - 200: A JSON object with a success message if the task is successfully deleted.
                - 401: If the JWT token is invalid or the email is not found.
                - 404: If the user or task is not found or the task does not belong to the user.
                - 500: If there is an internal server error.
    """
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
