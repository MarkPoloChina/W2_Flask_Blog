from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash  # used for password hash and check
from flask_login import UserMixin  # used for login check
from app import login  # used for loading info from databases
from hashlib import md5

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120),index=True,unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    comments = db.relationship('Comment',backref='author',lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<用户名:{}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(20))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.now)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    video_id = db.Column(db.String(50))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Liked(db.Model):
    __tablename__ = 'liked'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.now)
    liked = db.relationship('Post',backref='liked')

    def __repr__(self):
        return '<Liked {}>'.format(self.post_id)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.now)

    def __repr__(self):
        return '<Comment {}>'.format(self.body)


class Tagged(db.Model):
    __tablename__ = 'tagged'
    id = db.Column(db.Integer,primary_key=True)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    body = db.Column(db.String(10))

    def __repr__(self):
        return '<Tagged {}>'.format(self.body)


class Collected(db.Model):
    __tablename__ = 'collected'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.now)
    collected = db.relationship('Post',backref='collected')

    def __repr__(self):
        return '<Collected {}>'.format(self.post_id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))