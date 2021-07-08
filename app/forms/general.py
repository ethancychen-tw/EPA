from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, SelectMultipleField, RadioField, widgets
from wtforms.fields.html5 import DateField, EmailField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models.user import User

import datetime

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ReviewForm(FlaskForm):
    implement_date = DateField(label="實作時間", validators=[DataRequired()], default=datetime.date.today())
    location = SelectField(label='實作地點', choices=[('', '')], default='')
    epa = SelectField(label='EPA', choices=[('', '')], default='')
    reviewee = SelectField(label="學生", choices=[('', '')], default='')
    reviewer = SelectField(label='老師', choices=[('', '')], default='')
    review_difficulty = SelectField(label='(1) 這項工作的複雜程度為')
    review_compliment = TextAreaField(label="(2) 我覺得你表現不錯的地方在" ,validators=[DataRequired()])
    review_suggestion = TextAreaField(label="(3) 如果你能做到以下建議，就可以獲得老師或病人更高的信任" , validators=[DataRequired()])
    review_score = SelectField(label='(4) 如果下次再遇到類似情形，我對你的信賴等級為')
    submit = SubmitField('提交')

    review_source = SelectField(label='來源', choices=[('', '')], default='')
    complete = SelectField(label="已完成", choices=[('True', '是'),('False','否')], default='False')
    create_time = DateTimeLocalField(label='創建時間', format='%Y-%m-%dT%H:%M')
    last_edited = DateTimeLocalField(label='最近更新時間',format='%Y-%m-%dT%H:%M')

    
    @property
    def requesting_fields(self):
        return [self.epa, self.reviewer, self.reviewee, self.location, self.implement_date ]
    
    @property
    def scoring_fields(self):
        return [self.review_difficulty, self.review_compliment, self.review_suggestion, self.review_score]
    
    @property
    def meta_fields(self):
        return [self.review_source, self.complete, self.create_time, self.last_edited]    

class LoginForm(FlaskForm):
    username = StringField("姓名" ,validators=[DataRequired()])
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
    password = PasswordField(label="密碼", validators=[DataRequired("這是必填項目")])
    password2 = PasswordField(label="密碼確認", validators=[DataRequired("這是必填項目"), EqualTo('password', message='密碼兩次填寫不一致')])
    submit = SubmitField(label='送出')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('這個姓名已被使用')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('這個email已被使用')
class EditProfileForm(FlaskForm):
    
    bindline = BooleanField(label="Line帳號")
    email = EmailField("Email", validators=[DataRequired(), Email()])
    role = SelectField(label='職級', choices=[('', '')], default='')
    internal_group = SelectField(label="所屬醫院", validators=[DataRequired()])
    external_groups = SelectMultipleField(label="外派醫院", choices=[('', '')], default='')
    submit = SubmitField(label='更新並儲存')

class PasswdResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField('發送 email')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
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
    reviewees = MultiCheckboxField(label='學生', choices=[('', '')],  default=[''])
    reviewers = MultiCheckboxField(label='老師', choices=[('', '')], default=[''])
    groups = MultiCheckboxField(label='群組',choices=[('', '')], default=['']) # only available for manager
    create_time_start = DateField(label='創建時間開始', default=datetime.datetime.now()-datetime.timedelta(days=360))
    create_time_end = DateField(label='創建時間結束', default=datetime.datetime.now()+datetime.timedelta(days=1))
    complete = MultiCheckboxField(label='已完成', choices=[('True', '是'),('False','否')])
    epas = MultiCheckboxField(label='EPA', choices=[('', '')], default=[''])
    sort_key = RadioField(label="排序", choices=[('EPA','EPA'),('implement_date','實作時間'), ('create_time','創建時間')], validators=[DataRequired()], default='EPA')
    submit = SubmitField(label='篩選')
