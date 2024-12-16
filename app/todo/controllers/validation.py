import re
from app.todo.models.users import User
from app.todo.controllers.services import find_user

class FieldValidations:
    def email_validation(self,email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    def find_password(self,password,email):
        try:
            user_obj = [i.password  for i in find_user(email)]
            if user_obj[0].lower() == password.lower():
                return True
            else:
                return False
        except Exception as error:
            print("message:",str(error))
    def find_email(self,email_id):
        try:
            email = User.query.filter_by(
               email=email_id
            )
            email_lis = [i.email for i in email]
            if email_lis[0] == email_id:
                return True
            else:
                return  False
        except Exception as error:
            print("message", str(error))
