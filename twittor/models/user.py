from datetime import datetime
from hashlib import md5
import time

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import jwt

from twittor import db, login_manager
from twittor.models.tweet import Tweet, Review
from twittor.models.fact import EPA, Location

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

user_group = db.Table('user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class Group(db.Model):
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    desc = db.Column(db.String(64))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(120))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_activated = db.Column(db.Boolean, default=False)

    tweets = db.relationship('Tweet', backref='author', lazy='dynamic')

    #### epa
    line_userId = db.Column(db.String(128))
    role = db.Column(db.String(20), default="student")
    # If you use backref you don't need to declare the relationship on the second table.
    make_reviews = db.relationship('Review', primaryjoin=Review.reviewer_id==id, backref='reviewer', lazy='dynamic')
    being_reviews = db.relationship('Review' ,primaryjoin=Review.reviewee_id==id, backref='reviewee', lazy='dynamic')
    groups = db.relationship('Group', secondary=user_group, backref="users", lazy='dynamic')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return 'id={}, username={}, email={}, password_hash={}'.format(
            self.id, self.username, self.email, self.password_hash
        )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=80):
        md5_digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(md5_digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def own_and_followed_tweets(self):
        followed = Tweet.query.join(
            followers, (followers.c.followed_id == Tweet.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Tweet.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Tweet.create_time.desc())

    def get_jwt(self, expire=300):
        return jwt.encode(
            {
                'email': self.email,
                'exp': time.time() + expire
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_jwt(token):
        try:
            email = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            email = email['email']
        except:
            return
        return User.query.filter_by(email=email).first()


@login_manager.user_loader
def load_user(id):
    """
    implement login_user method for flask_login
    this global function makes the login manager instance(in __init__.py) could get user instance in route
    """
    return User.query.get(int(id))
