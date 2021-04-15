from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Length

from twittor.models.user import User

class AskReviewForm(FlaskForm):
    location = SelectField(label='地點') # quick search text field?
    epa = SelectField(label='EPA') # quick search text field?
    requester = SelectField(label="請求者") # quick search text field?
    reviewer = SelectField(label='評核者') # quick search text field?
    submit = SubmitField(label='提交')

class ReviewForm(FlaskForm):
    location = SelectField(label='我在')
    epa = SelectField(label='EPA')
    reviewee = SelectField(label="被評核者")
    reviewer = SelectField(label='評核者')
    review_difficulty = SelectField(label='這項工作的難度', choices=[(1, '基本'), (2, '進階')])
    review_compliment = StringField(label="我覺得你表現不錯的地方是" ,validators=[DataRequired()])
    review_suggestion = StringField(label="我覺得你可以改進的地方" , validators=[DataRequired()])
    review_score = SelectField(label='整體來說，評分為', choices=[(0, '只能觀察，不能操作'), (4, '可指導別人')])
    submit = SubmitField('提交')


class LoginForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("Username" ,validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField("Username" ,validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Password Repeat", validators=[DataRequired(), EqualTo('password')])
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
