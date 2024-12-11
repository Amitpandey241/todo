import re
import app.todo.models.users import User
class FieldValidations:
    def email_validation(self,email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    def find_password(self,password,user_id):
        try:
            user_obj =
            if user_obj.password.lower() == password.lower():
                return True
            else:
                return False
        except Exception as error:
            print("message:",str(error))
