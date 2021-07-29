from datetime import datetime
from hashlib import md5
import time
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
    
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import jwt

from app import db, login_manager
from app.channels import linebot, gmail
from app.models.review import Review, ReviewSource

user_externalgroup = db.Table('user_externalgroup',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id')),
    db.Column('group_id', UUID(as_uuid=True), db.ForeignKey('groups.id'))
)

class Group(db.Model):
    __tablename__ = "groups"
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)   ## Be careful not to miss passing the callable uuid.uuid4 into the column definition, rather than calling the function itself with uuid.uuid4(). Otherwise, you will have the same scalar value for all instances of this class

    name = db.Column(db.String(64), unique=True, index=True)
    desc = db.Column(db.String(64))

    internal_users = db.relationship('User', backref="internal_group", lazy='dynamic')

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    
    can_be_reviewee = db.Column(db.Boolean(), default=False) # can request a review
    can_be_reviewer = db.Column(db.Boolean(), default=False) # can request a review

    # manager
    is_manager = db.Column(db.Boolean(), default=False) # a convient tag. can do anything for the internal group, or users being assign to manager's internal group
    users = db.relationship('User', backref='role', lazy='dynamic') # should use lazy='dynamic': load the required relation when it's called

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    create_time = db.Column(db.DateTime, default=datetime.utcnow) 
    account = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    internal_group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id')) 
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.id'))
    
    # If you use backref you don't need to declare the relationship on the second table.
    line_userId = db.Column(db.String(128))
    create_reviews = db.relationship('Review', primaryjoin=Review.creator_id==id, backref='creator', lazy='dynamic') 
    make_reviews = db.relationship('Review', primaryjoin=Review.reviewer_id==id, backref='reviewer', lazy='dynamic') # need to specify primary join, cuz there are more than one ways to join users and review
    being_reviews = db.relationship('Review' ,primaryjoin=Review.reviewee_id==id, backref='reviewee', lazy='dynamic') 
    external_groups = db.relationship('Group', secondary=user_externalgroup, backref="external_users", lazy='dynamic') # first specify the target
    notifications = db.relationship('Notification', backref="user", lazy='dynamic') # first specify the target

    def __repr__(self):
        return f'id={self.id}, account={self.account}, username={self.username}, email={self.email}, line_id={self.line_userId}'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def send_message(self,subject="", msg_body="",channels=None):
        """
        notify user via line and email
        """
        if not channels:
            channels = ['email']
        for channel in channels:
            if channel == 'line' and self.line_userId:
                try:
                    linebot.send_line(self.line_userId, subject, msg_body)
                except Exception as e:
                    print(e)
            if channel == 'email' and self.email:
                try:
                    gmail.send_email(recipients=[self.email], subject=subject, text_body=msg_body)
                except Exception as e:
                    print(e)
        

    def avatar(self):
        img_src = None
        if self.line_userId:
            try:
                line_user_profile = linebot.line_bot_api.get_profile(self.line_userId)
                img_src = line_user_profile.picture_url
            except Exception as e:
                print("can't get line profile")
                print(e)
        else:
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
    def can_view_review(self, review=None):
        if self.role.is_manager:
            return True
        # 發起人一定能看，不論狀態
        if review.creator == self:
            return True
        # 相關人只能在非draft狀態下看
        if not review.is_draft and (self ==review.reviewer or self == review.reviewee):
            return True
        return False

    def can_create_review(self):
        return self.role.can_be_reviewer
    
    def can_request_review(self):
        return self.role.can_be_reviewee

    def can_edit_review(self, review=None):
        if self.role.is_manager:
            return True
        if not self.can_view_review(review):
            return False
        
        # 發起人在draft狀態下一定能編輯
        if review.creator == self and review.is_draft and not review.complete:
            return True
        if review.reviewer == self:
            return True
        return False

    def can_delete_review(self, review=None):
        if self.role.is_manager:
            return True
        if not self.can_view_review(review):
            return False
        if review.complete:
            return False
        if review.creator == self and review.is_draft:
            return True
        # 是學生發起的話，學生只要非完成都可以刪(即便老師正暫存他的評核)
        if review.creator == self and not review.is_draft and not review.complete:
            return True
        return False
    
    def get_potential_reviewees(self):
        if self.role.can_be_reviewer:
            internal_users = self.internal_group.internal_users.all() #本身就在和老師相同所屬醫院的內部成員
            been_sent_to_internal_users = self.internal_group.external_users # 被外派到和老師相同所屬醫院的成員
            unique_users = list(set(internal_users+been_sent_to_internal_users))
            return [user for user in unique_users if not user.role.is_manager and user !=self and user.role.can_be_reviewee]
        else:
            return []
    
    def get_potential_reviewers(self):
        if self.role.can_be_reviewee:
            internal_users = self.internal_group.internal_users.all() #本身就在和學生相同醫院的內部成員
            external_users = [ext_group.internal_users.all() for ext_group in self.external_groups] # 在外派醫院的內部成員
            external_users = [item for sublist in external_users for item in sublist]
            unique_users = list(set(internal_users+external_users))
            return [user for user in unique_users if not user.role.is_manager and user != self and user.role.can_be_reviewer]
        else:
            return []
    
    def get_draft_request_reviews(self, role=None):
        # std draft request
        if not self.can_request_review():
            return []
        return Review.query.filter(Review.creator_id == self.id, Review.reviewee_id == self.id, Review.complete==False, Review.is_draft == True).all()

    def get_unfin_request_reviews(self):
        # as a std. std submit request, teacher unfin
        if not self.can_request_review():
            return []
        return Review.query.filter(Review.creator_id == self.id, Review.reviewee_id == self.id, Review.complete==False, Review.is_draft == False).all()

    def get_draft_reviews(self):
        # teacher draft review directly
        if not self.can_create_review():
            return []
        return Review.query.filter(Review.creator_id == self.id, Review.reviewer_id == self.id, Review.complete==False, Review.is_draft == True).all()

    def get_unfin_reviews(self):
        # as a teacher. std submit request, teacher unfin
        if not self.can_create_review:
            return []
        return Review.query.filter(Review.creator_id != self.id, Review.reviewer_id == self.id, Review.complete==False, Review.is_draft == False).all()

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    subject = db.Column(db.String(64))
    msg_body = db.Column(db.String(256))
    UniqueConstraint('user_id', 'subject', 'msg_body', name='unique_notification')
class LineNewUser(db.Model):
    __tablename__ = "line_new_users"
    id = db.Column(db.Integer, primary_key=True)
    line_userId = db.Column(db.String(64))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def get_jwt(self, expire=180):
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
            return False
        return LineNewUser.query.filter(LineNewUser.line_userId==line_userId).order_by(LineNewUser.create_time.desc()).first()
    

@login_manager.user_loader
def load_user(id):
    """
    implement login_user method for flask_login
    this global function makes the login manager instance(in __init__.py) could get user instance in route
    """
    return User.query.get(id)
