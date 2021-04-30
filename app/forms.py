from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Length

from app.models.user import User

import datetime
class ReviewForm(FlaskForm):
    implement_date = DateField(label="實作時間", validators=[DataRequired()], default=datetime.date.today())
    location = SelectField(label='我在')
    epa = SelectField(label='EPA')
    reviewee = SelectField(label="被評核者")
    reviewer = SelectField(label='評核者')
    review_difficulty = SelectField(label='這項工作的難度')
    review_compliment = TextAreaField(label="我覺得你表現不錯的地方是" ,validators=[DataRequired()])
    review_suggestion = TextAreaField(label="我覺得你可以改進的地方" , validators=[DataRequired()])
    review_score = SelectField(label='整體來說，評分為')
    submit = SubmitField('提交')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("Username" ,validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField('Sign In')

class LineActivateForm(FlaskForm):
    submit = SubmitField('activate')

class RegisterForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("Username" ,validators=[DataRequired()])
    bindline = BooleanField(label="linebind", default=False)
    role = SelectField(label='role', validators=[DataRequired()])
    groups = SelectMultipleField(label="groups", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Password Repeat", validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('please use different username')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('please use different email address')


class EditProfileForm(FlaskForm):
    about_me = TextAreaField('About me', validators=[Length(min=0, max=120)])
    submit = SubmitField('Save')


class TweetForm(FlaskForm):
    tweet = TextAreaField('Tweet', validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Tweet')


class PasswdResetRequestForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError(
                'You do not have an account for this email address')


class PasswdResetForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Password Repeat", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')
