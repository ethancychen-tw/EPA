from datetime import datetime
from hashlib import md5
import time

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import jwt

from twittor import db, login_manager
from twittor.models.tweet import  Review

user_group = db.Table('user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

class Group(db.Model):
    __tablename__ = "groups"
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    desc = db.Column(db.String(64))

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    
    users = db.relationship('User', backref='role', lazy='dynamic')

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_activated = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    # If you use backref you don't need to declare the relationship on the second table.
    line_userId = db.Column(db.String(128))
    make_reviews = db.relationship('Review', primaryjoin=Review.reviewer_id==id, backref='reviewer', lazy='dynamic') # need to specify primary join, cuz there are more than one ways to join users and review
    being_reviews = db.relationship('Review' ,primaryjoin=Review.reviewee_id==id, backref='reviewee', lazy='dynamic') 
    groups = db.relationship('Group', secondary=user_group, backref="users", lazy='dynamic') # first specify the target
    

    # followed = db.relationship(
    #     'User', secondary=followers,
    #     primaryjoin=(followers.c.follower_id == id),
    #     secondaryjoin=(followers.c.followed_id == id),
    #     backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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

    def get_jwt(self, expire=300):
        return jwt.encode(
            {
                'line_userId': self.line_userId,
                'exp': time.time() + expire
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_jwt(token):
        try:
            pay_load = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            line_userId = pay_load['line_userId']
        except:
            return
        return User.query.filter_by(line_userId=line_userId).first()


@login_manager.user_loader
def load_user(id):
    """
    implement login_user method for flask_login
    this global function makes the login manager instance(in __init__.py) could get user instance in route
    """
    return User.query.get(int(id))
