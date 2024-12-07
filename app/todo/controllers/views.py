from flask import Flask, make_response, jsonify, request, Blueprint
from flask_restful import Resource, Api
from app import api, db

todo_blueprint = Blueprint("todo", __name__)

class HealthCheck(Resource):
    def get(self):
        try:
            return make_response(jsonify({"message": "THis is health check api"}))
        except Exception as error:
            return make_response(jsonify({"message": str(error)}))


api.add_resource(HealthCheck, "/v1/api/health/")