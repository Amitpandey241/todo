import pytest
from flask import json
from app.todo.models import User, Tasks
from app import db


@pytest.fixture
def setup_user_and_tasks(init_database):
    # this is for emiting test case data
    user = User(email="pamit@gmail.com", password="test123")
    db.session.add(user)
    db.session.commit()

    task1 = Tasks(title="Task 1", description="First Task", is_completed=False, user_id=user.id)
    task2 = Tasks(title="Task 2", description="Second Task", is_completed=True, user_id=user.id)

    db.session.add_all([task1, task2])
    db.session.commit()

    return user, [task1, task2]


#this is for health check api
def test_health_check(client):
    response = client.get("/v1/api/health/")
    assert response.status_code == 200
    assert response.json["message"] == "THis is health check api"

