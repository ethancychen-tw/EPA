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

class RegisterForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("姓名" ,validators=[DataRequired()])
    bindline = BooleanField(label="綁定我的line帳號", default=False)
    role = SelectField(label='身份/職級', validators=[DataRequired()])
    internal_group = SelectField(label="所屬醫院/群組", validators=[DataRequired()])
    external_groups = SelectMultipleField(label="外派醫院/群組(可複選)")
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="密碼", validators=[DataRequired()])
    password2 = PasswordField(label="密碼確認", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='送出')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('please use different username')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('please use different email address')


class EditProfileForm(FlaskForm):
    bindline = BooleanField(label="bindline")
    role = SelectField(label='role', validators=[DataRequired()])
    internal_group = SelectMultipleField(label="internal_group", validators=[DataRequired()])
    external_groups = SelectMultipleField(label="external_groups", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField('Save')

class PasswdResetRequestForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError(
                'You do not have an account for this email address')


class PasswdResetForm(FlaskForm):
    password = PasswordField(label="Password", validators=[DataRequired()])
    password2 = PasswordField(label="Password Repeat", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Submit')
