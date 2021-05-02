from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Length

from app.models.user import User

import datetime
class ReviewForm(FlaskForm):
    review_source = SelectField(label='來源', choices=[('', '')], default='')
    implement_date = DateField(label="實作時間", validators=[DataRequired()], default=datetime.date.today())
    location = SelectField(label='實作地點', choices=[('', '')], default='')
    epa = SelectField(label='EPA', choices=[('', '')], default='')
    reviewee = SelectField(label="被評核者", choices=[('', '')], default='')
    reviewer = SelectField(label='評核者', choices=[('', '')], default='')
    review_difficulty = SelectField(label='(1) 這項工作的複雜程度為')
    review_compliment = TextAreaField(label="(2) 我覺得你表現不錯的地方在" ,validators=[DataRequired()])
    review_suggestion = TextAreaField(label="(3) 如果你能做到以下建議，就可以獲得老師或病人更高的信任" , validators=[DataRequired()])
    review_score = SelectField(label='(4) 如果下次再遇到類似情形，我對你的信賴等級為')
    submit = SubmitField('提交')

    @property
    def requesting_fields(self):
        return [self.implement_date, self.location, self.epa, self.reviewee, self.reviewer]
    
    @property
    def scoring_fields(self):
        return [self.implement_date, self.location, self.epa, self.reviewee, self.reviewer]
    


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
    
    bindline = BooleanField(label="Line帳號")
    email = EmailField("Email", validators=[DataRequired(), Email()])
    role = SelectField(label='職級', validators=[DataRequired()])
    internal_group = SelectField(label="所屬醫院", validators=[DataRequired()])
    external_groups = SelectMultipleField(label="外派醫院", validators=[DataRequired()])
    submit = SubmitField(label='更新並儲存')

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
