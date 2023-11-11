from flask import Blueprint,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from src.models import Bookmark
from src.constants import http_status as status
import validators
from src.models import db,Bookmark
from flasgger import swag_from





bookmarks = Blueprint("bookmarks",__name__,url_prefix="/bookmarks")

@bookmarks.get("/me")
@jwt_required()
def my_bookmarks():
    user_id = get_jwt_identity()
    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",10,type=int)
    bookmarks = Bookmark.query.filter_by(user_id=user_id).paginate(page=page,per_page=per_page)
    bookmarks_dict = []
    for bookmark in bookmarks:
        bookmark_dict = bookmark.__dict__
        del bookmark_dict['_sa_instance_state']
        bookmarks_dict.append(bookmark_dict)
    return jsonify({"bookmarks": bookmarks_dict,
                    "meta":{
                            "page":bookmarks.page,
                            "per_page":bookmarks.per_page,
                            "total":bookmarks.total,
                            "next": bookmarks.next_num,
                            "prev": bookmarks.prev_num,
                            "has_nest": bookmarks.has_next,
                            "has_prev": bookmarks.has_prev,
                   }}), status.HTTP_200_OK



@bookmarks.post("/add")
@jwt_required()
@swag_from("./docs/bookmarks/add_bookmark.yml")
def add_bookmark():
    user_id = get_jwt_identity()
    url = request.json.get("url")
    description = request.json.get("description","")

    if validators.url(url) == False:
        return {"message":"Invalid URL"},status.HTTP_400_BAD_REQUEST
    
    if Bookmark.query.filter_by(url=url,user_id=user_id).first():
        return {"message":"Bookmark already exists"},status.HTTP_409_CONFLICT
    

    bookmark = Bookmark(url=url,user_id=user_id,description=description)
    db.session.add(bookmark)
    db.session.commit()
    return {"message":"Bookmark added"},status.HTTP_201_CREATED


@bookmarks.get("/<id>")
@jwt_required()
def get_bookmark(id):
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id,user_id=user_id).first()
    if bookmark:
        return {"bookmark":{
            "url":bookmark.url,
            "description":bookmark.description,
        }
        },status.HTTP_200_OK

    else:
        return {"message":"Bookmark not found"},status.HTTP_404_NOT_FOUND
    

@bookmarks.put("/<id>")
@jwt_required()
def update_bookmark(id):
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id,user_id=user_id).first()
    if bookmark:
        bookmark.url = request.json.get("url",bookmark.url)
        bookmark.description = request.json.get("description",bookmark.description)
        db.session.commit()
        return {"message":"Bookmark updated"},status.HTTP_200_OK
    else:
        return {"message":"Bookmark not found"},status.HTTP_404_NOT_FOUND
    


@bookmarks.delete("/<id>")
@jwt_required()
def delete_bookmark(id):
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id,user_id=user_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return {"message":"Bookmark deleted"},status.HTTP_200_OK
    else:
        return {"message":"Bookmark not found"},status.HTTP_404_NOT_FOUND
    


@bookmarks.get("/stats")
@jwt_required()
def stats():
    user_id = get_jwt_identity()
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    data = []
    
    for bookmark in bookmarks:
        new_link ={
            'visits':bookmark.visits,
            'url':bookmark.url,
            'short_url': f'http://localhost:5000/{bookmark.short_url}'   
        }
        data.append(new_link)

    return jsonify({"data":data}),status.HTTP_200_OK









