from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SelectField
from wtforms.fields.html5 import  DateTimeLocalField, EmailField
from wtforms.validators import DataRequired, Email

import datetime

class AdminEditProfileForm(FlaskForm):
    bindline = BooleanField(label="Line帳號")
    email = EmailField("Email", validators=[DataRequired(), Email()])
    role = SelectField(label='職級', choices=[('', '')], default='')
    internal_group = SelectField(label="所屬醫院", validators=[DataRequired()])
    external_groups = SelectMultipleField(label="外派醫院", choices=[('', '')], default='')
    create_time = DateTimeLocalField(label='創建時間', validators=[DataRequired()])
    username = StringField(label='姓名', validators=[DataRequired()])
    password = PasswordField(label="密碼", validators=[DataRequired("這是必填項目")])
    is_activated = BooleanField(label="已啟用")
    line_userId = StringField(label='Line使用者代碼', validators=[DataRequired()])

class NewGroupForm(FlaskForm):
    name = StringField(label='群組名稱', validators=[DataRequired()])
    desc = StringField(label='描述', validators=[DataRequired()])
    internal_users = SelectMultipleField(label='院內成員')
    external_users = SelectMultipleField(label='外派至此院之成員')

class NewEPAForm(FlaskForm):
    name = StringField(label='EPA名稱', validators=[DataRequired()])
    desc = StringField(label='描述', validators=[DataRequired()])
    milestones = SelectMultipleField(label='對應的 Milestone 項目')