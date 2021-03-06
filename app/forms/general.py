from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, SelectMultipleField, RadioField, widgets
from wtforms.fields.html5 import DateField, EmailField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional

from app.models.user import User

import datetime
class ReviewForm(FlaskForm):
    # requesting fields
    epa = SelectField(label='EPA',choices=[('','')], default='')
    reviewer = SelectField(label='老師',choices=[('','')], default='')
    reviewee = SelectField(label="學生",choices=[('','')], default='')
    location = SelectField(label='實作地點',choices=[('','')], default='')
    implement_date = DateField(label="實作時間", validators=[DataRequired()], default=datetime.date.today())
    reviewee_note = TextAreaField(label="學生備註" )

    # scoring fields
    review_difficulty = SelectField(label='(1) 這項工作的複雜程度為',choices=[('','')], default='')
    review_compliment = TextAreaField(label="(2) 我覺得你表現不錯的地方在" )
    review_suggestion = TextAreaField(label="(3) 如果你能做到以下建議會更好" )
    review_score = RadioField(label='(4) 我對你的信賴等級為',choices=[('','')], default='')

    # btns
    submit = SubmitField(label='提交')
    submit_draft = SubmitField(label='暫存')

    # meta
    creator = SelectField(label="創建者", choices=[('', '')], default='')
    review_source = SelectField(label='來源', choices=[('', '')], default='')
    complete = SelectField(label="已完成", choices=[('True', '是'),('False','否')], default='False')
    create_time = DateTimeLocalField(label='創建時間', format='%Y-%m-%dT%H:%M')
    last_edited = DateTimeLocalField(label='最近更新時間',format='%Y-%m-%dT%H:%M')

    @property
    def btns(self):
        return [self.submit, self.save_draft]
        
    @property
    def requesting_fields(self):
        return [self.epa, self.reviewer, self.reviewee, self.location, self.implement_date, self.reviewee_note ]
    
    @property
    def scoring_fields(self):
        return [self.review_difficulty, self.review_compliment, self.review_suggestion, self.review_score]
    
    @property
    def meta_fields(self):
        return [self.creator, self.review_source, self.complete, self.create_time, self.last_edited]    

class LoginForm(FlaskForm):
    account = StringField("帳號", validators=[DataRequired()])
    password = PasswordField("密碼", validators=[DataRequired()])
    remember_me = BooleanField("記住我")
    submit = SubmitField('登入')

class RegisterForm(FlaskForm):
    username = StringField("姓名" ,validators=[DataRequired()])
    bindline = BooleanField(label="綁定我的line帳號", default=False)
    role = SelectField(label='身份/職級', validators=[DataRequired()])
    internal_group = SelectField(label="所屬醫院/群組", validators=[DataRequired("至少要選一間醫院")])
    external_groups = SelectMultipleField(label="外訓醫院/群組(可複選)")
    email = EmailField(label="Email", validators=[DataRequired("這是必填項目"), Email()])
    account = StringField("帳號", validators=[DataRequired()])
    password = PasswordField(label="密碼", validators=[DataRequired("這是必填項目")])
    password2 = PasswordField(label="密碼確認", validators=[DataRequired("這是必填項目"), EqualTo('password', message='密碼兩次填寫不一致')])
    submit = SubmitField(label='送出')

    def validate_account(self, account):
        user = User.query.filter(User.account==account.data).first()
        if user is not None:
            raise ValidationError('這個帳號已被使用')
    
    def validate_email(self, email):
        user = User.query.filter(User.email==email.data).first()
        if user is not None:
            raise ValidationError('這個email已被使用')

    def validate_external_groups(self, external_groups):
        if self.internal_group.data in external_groups.data:
            raise ValidationError('外訓醫院不可包含所屬醫院')
    
class EditProfileForm(FlaskForm):
    bindline = BooleanField(label="Line帳號")
    account = StringField("帳號")
    role = SelectField(label='職級', choices=[('', '')], default='')
    username = StringField("姓名", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email("Email格式不正確")])
    internal_group = SelectField(label="所屬醫院", validators=[DataRequired()])
    external_groups = SelectMultipleField(label="外訓醫院", choices=[('', '')], default='')
    submit = SubmitField(label='更新並儲存')

    def validate_external_groups(self, external_groups):
        if self.internal_group.data in external_groups.data:
            raise ValidationError('外訓醫院不可包含所屬醫院')
    
    def validate_email(self, email):
        user = User.query.filter(email==email.data).first()
        if user is not None:
            raise ValidationError('這個email已被使用')

class PasswdResetRequestForm(FlaskForm):
    account = StringField("帳號", validators=[Optional()])
    email = StringField("Email (與帳號擇一填寫即可)", validators=[Optional(), Email()])
    submit = SubmitField('發送 email')

    def validate_account(self, account):
        user = User.query.filter(User.account==account.data).first()
        if not user:
            raise ValidationError('沒有此帳號')

    def validate_email(self, email):
        user = User.query.filter(User.email==email.data).first()
        if not user:
            raise ValidationError('沒有帳號註冊此 Email')


class PasswdResetForm(FlaskForm):
    password = PasswordField(label="新密碼", validators=[DataRequired()])
    password2 = PasswordField(label="新密碼確認", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='提交')
    
class UserFilterForm(FlaskForm):
    groups = SelectMultipleField()
    show_user_tpyes = SelectMultipleField(label='成員類型', choices=[('internal_users', '所屬醫院')])
    role = SelectMultipleField(label='職級/角色', choices=[('', '')], default=[''])

class ReviewFilterForm(FlaskForm):
    reviewees = SelectMultipleField(label='學生(可複選)', choices=[])
    reviewers = SelectMultipleField(label='老師(可複選)', choices=[])
    groups = SelectMultipleField(label='醫院(可複選)', choices=[]) # only available for manager
    implement_date_start = DateField(label='實作時間開始', default=datetime.datetime.now()-datetime.timedelta(days=360), validators=[DataRequired()])
    implement_date_end = DateField(label='實作時間結束', default=datetime.datetime.now()+datetime.timedelta(days=1), validators=[DataRequired()])
    epas = SelectMultipleField(label='EPA', choices=[])
    sort_key = RadioField(label="排序", choices=[('EPA','EPA'),('implement_date','實作時間')], validators=[DataRequired()], default='EPA')
    submit = SubmitField(label='篩選')
