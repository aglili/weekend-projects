import validators
from src.models import User


def validate_user(user_info):
    errors = {}
    username = user_info.get("username")
    email = user_info.get("email")
    password = user_info.get("password")

    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters"
    
    if len(username) < 3:
        errors["username"] = "Username must be at least 3 characters"
    
    if username.isalnum() == False:
        errors["username"] = "Username must be alphanumeric"
    
    if " " in username:
        errors["username"] = "Username must not contain spaces"
    

    if validators.email(email) == False:
        errors["email"] = "Email is not valid"
    
    if User.query.filter_by(email=email).first():
        errors["email"] = "Email is already taken"
    
    if User.query.filter_by(username=username).first():
        errors["username"] = "Username is already taken"
    
    is_valid = len(errors) == 0
    
    return is_valid, errors