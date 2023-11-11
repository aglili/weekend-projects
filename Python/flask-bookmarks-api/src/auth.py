from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from src.constants import http_status as status
import validators
from src.models import User,db
from src.utils import validate_user
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity
from flasgger import swag_from



auth  = Blueprint('auth',__name__,url_prefix='/auth')


@auth.post("/sign-up")
@swag_from("./docs/auth/signup.yml")
def sign_up():
    is_valid, errors = validate_user(request.json)
    if is_valid:
        user = User(
            username=request.json.get("username"),
            email=request.json.get("email"),
            password=generate_password_hash(request.json.get("password"))
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"User Created","user_info":{
            "username":user.username,
            "email":user.email,
        }}),status.HTTP_201_CREATED
    else:
        return jsonify(errors),status.HTTP_400_BAD_REQUEST



@auth.post("/sign-in")
@swag_from("./docs/auth/login.yml")
def sign_in():
    email = request.json.get("email",None)
    password = request.json.get("password",None)
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password,password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify({"message":"User logged in","user_info":{
            "username":user.username,
            "access_token":access_token,
            "refresh_token":refresh_token
        }}),status.HTTP_200_OK
    else:
        return jsonify({"message":"Invalid credentials"}),status.HTTP_401_UNAUTHORIZED
    

@auth.post("token/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token":access_token}),status.HTTP_200_OK



@auth.get("/user")
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    return jsonify({"user_info":{
        "username":user.username,
        "email":user.email
    }}),status.HTTP_200_OK
