from doctest import debug

from app.todo.controllers.views import todo_blueprint
from flask import Blueprint
from app import app

app.register_blueprint(todo_blueprint)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")