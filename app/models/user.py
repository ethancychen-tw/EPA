from datetime import datetime
from hashlib import md5
import time

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import jwt

from app import db, login_manager, line_bot_api
from app.models.review import Review

user_externalgroup = db.Table('user_externalgroup',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)

class Group(db.Model):
    __tablename__ = "groups"
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    desc = db.Column(db.String(64))

    internal_users = db.relationship('User', backref="internal_group", lazy='dynamic')

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    
    can_request_review = db.Column(db.Boolean(), default=False) # can request a review
    can_create_and_edit_review = db.Column(db.Boolean(), default=False) # can create, edit, del a review if reviewer

    # manager, admin
    is_manager = db.Column(db.Boolean(), default=False) # can do anything

    users = db.relationship('User', backref='role', lazy='dynamic')

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_activated = db.Column(db.Boolean, default=False)
    internal_group_id = db.Column(db.Integer, db.ForeignKey('groups.id')) 
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    # If you use backref you don't need to declare the relationship on the second table.
    line_userId = db.Column(db.String(128))
    make_reviews = db.relationship('Review', primaryjoin=Review.reviewer_id==id, backref='reviewer', lazy='dynamic') # need to specify primary join, cuz there are more than one ways to join users and review
    being_reviews = db.relationship('Review' ,primaryjoin=Review.reviewee_id==id, backref='reviewee', lazy='dynamic') 
    external_groups = db.relationship('Group', secondary=user_externalgroup, backref="external_users", lazy='dynamic') # first specify the target

    def __repr__(self):
        return 'id={}, username={}, email={}, password_hash={}'.format(
            self.id, self.username, self.email, self.password_hash
        )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        img_src = None
        if not img_src and self.line_userId:
            try:
                line_user_profile = line_bot_api.get_profile(self.line_userId)
                img_src = line_user_profile.picture_url
            except Exception as e:
                print("can't get line profile")
                print(e)
        if not img_src:
            try:
                md5_digest = md5(self.email.lower().encode('utf-8')).hexdigest()
                img_src = f'https://www.gravatar.com/avatar/{md5_digest}?d=identicon&s=40'
            except Exception as e:
                print("can't get gravatar")
                print(e)
        return img_src

    def get_jwt(self, expire=300):
        return jwt.encode(
            {
                'email': self.email,
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
            email = pay_load['email']
            line_userId = pay_load['line_userId']
        except:
            return
        return User.query.filter(User.email==email).first()
    
    # should refactor using role auth
    def can_remove_review(self, review=None):
        if self.role.is_manager:
            return True
        if review.reviewer==self or review.reviewee == self:
            if review.complete:
                return True
            else:
                # for now, those who can make a review could edit/del the review
                return review.reviewer == self and self.role.can_create_and_edit_review 
        return False

    def can_edit_review(self, review=None):
        return self.role.is_manager or ( review.reviewer == self and self.role.can_create_and_edit_review)


@login_manager.user_loader
def load_user(id):
    """
    implement login_user method for flask_login
    this global function makes the login manager instance(in __init__.py) could get user instance in route
    """
    return User.query.get(int(id))
