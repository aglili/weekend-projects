from flask import Flask,jsonify,redirect
from dotenv import load_dotenv
import os
from src.bookmarks import bookmarks
from src.auth import auth
from src.database import db
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from src.models import Bookmark
from flasgger import Swagger,swag_from
from src.config.swagger import template,swagger_config



load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)
    

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI'),
            JWT_SECRET_KEY=os.getenv('SECRET_KEY'),

            SWAGGER = {
                "title":"BookmarksAPI",
                "uiversion":3
            }
        )
    else:
        app.config.from_mapping(test_config)
        
    db.app = app
    db.init_app(app)

    JWTManager(app)
    Migrate(app,db)
    app.register_blueprint(bookmarks)
    app.register_blueprint(auth)


    @app.get("/<short_url>")
    @swag_from("./docs/short_url.yml")
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        if bookmark:
            bookmark.visits += 1
            db.session.commit()
            return redirect(bookmark.url)
        else:
            return jsonify({"message":"URL not found"}),404
        


    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"message":"URL not found"}),404
    

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"message":"Internal Server Error"}),500
     



    Swagger(app=app,config=swagger_config,template=template)
    return app