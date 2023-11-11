from .database import db
from datetime import datetime
import uuid




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    password = db.Column(db.Text(),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now())
    bookmarks = db.relationship("Bookmark",backref="user",lazy=True)



    def __str__(self) -> str:
        return f"<User: {self.username}>"
    


class Bookmark(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    description = db.Column(db.Text(), nullable=True)
    url = db.Column(db.Text(), nullable=False)
    short_url = db.Column(db.String(6), nullable=False, unique=True)
    visits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def generate_short_url(self):
        url = uuid.uuid4().hex[:6].upper()
        link = self.query.filter_by(short_url=url).first()
        if link:
            return self.generate_short_url()
        return url

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.short_url = self.generate_short_url()

    def __str__(self) -> str:
        return f"<Bookmark: {self.url}>"
