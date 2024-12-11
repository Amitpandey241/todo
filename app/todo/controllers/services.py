from app.todo.models.users import User
from app.todo.models.tasks import Tasks

def find_user(email):
    try:
        user_obj = User.query.filter_by(
            email=email
        )
        return user_obj
    except Exception as error:
        print("message:", )