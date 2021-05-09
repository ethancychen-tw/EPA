import datetime

from flask import render_template, redirect, url_for, request, \
    abort, current_app, flash, Markup
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from app.forms import LoginForm, RegisterForm, EditProfileForm, \
    PasswdResetRequestForm, PasswdResetForm, ReviewForm
from app.models.user import User, load_user, Group, Role, LineNewUser
from app.models.review import Review, EPA, Location, ReviewDifficulty, ReviewScore, ReviewSource
from app import db
from app import line_bot_api, handler
from app.email import send_email


@login_required
def inspect_review(review_id):
    """
    see only, can't edit
    only reviewer or reviewee could see
    """
    prefilled_review = Review.query.get(review_id)
    if current_user.id not in [prefilled_review.reviewer.id, prefilled_review.reviewee.id]:
        flash('您沒有權限存取這個評核','alert-warning')
        return redirect(url_for('index'))
    
    # (1) form configuration
    form = ReviewForm()
    for field in form:
        field.render_kw = {'disabled': 'disabled'}
    
    # (2) on submit handle (not applicable here)
    # (3) prefill
    form.review_source.choices = [("",prefilled_review.review_source.desc)]
    form.reviewer.choices = [( "" ,prefilled_review.reviewer.username)]
    form.reviewee.choices = [( "" ,prefilled_review.reviewee.username)]
    form.location.choices = [( "" ,prefilled_review.location.desc)]
    form.implement_date.data = prefilled_review.implement_date
    form.epa.choices = [("" ,prefilled_review.epa.desc)]
    form.review_compliment.data = prefilled_review.review_compliment
    form.review_suggestion.data = prefilled_review.review_suggestion
    form.review_difficulty.choices = [("" ,prefilled_review.review_difficulty.desc if prefilled_review.review_score else "")]
    form.review_score.choices = [("", prefilled_review.review_score.desc if prefilled_review.review_score else "") ]
    return render_template('make_review.html', title="查看評核", form=form, review=prefilled_review, review_type="inspect")

@login_required
def edit_review(review_id):
    prefilled_review = Review.query.get(review_id)
    if prefilled_review.reviewer.id != current_user.id:
        flash('您沒有權限存取這個評核','alert-warning')
        return redirect(url_for('index'))
    # (1) form configuration
    form = ReviewForm()
    form.review_difficulty.choices = [(str(review_difficulty.id), review_difficulty.desc) for review_difficulty in ReviewDifficulty.query.all()]
    form.review_score.choices = [(str(review_score.id), review_score.desc) for review_score in ReviewScore.query.all()]
    for field in form.requesting_fields:
        field.render_kw = {'disabled':'disabled'}
    # (2) on submit process
    if form.validate_on_submit():
        review = prefilled_review
        review.review_compliment = form.review_compliment.data
        review.review_suggestion = form.review_suggestion.data
        review.review_difficulty = ReviewDifficulty.query.get(int(form.review_difficulty.data))
        review.review_score = ReviewScore.query.get(int(form.review_score.data))
        review.last_edited = datetime.datetime.now()
        review.complete = True
        subject = "[EPA通知]您已被評核"
        msg_body = f'{review.reviewee.username}你好，\n{review.reviewer.username}已評核你於{review.implement_date.strftime("%Y-%m-%d")}實作的{review.epa.desc}，你可前往系統查看'
        try:
            review.reviewee.send_message(subject=subject, msg_body=msg_body)
        except Exception as e:
            print(e)
        return redirect(url_for('index'))
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('index'))
    
    # (3) prefill (if have)
    
    form.reviewer.choices = [("" ,prefilled_review.reviewer.username)]
    form.reviewee.choices = [("" ,prefilled_review.reviewee.username)]
    form.location.choices = [("" ,prefilled_review.location.desc)]
    form.epa.choices = [("" ,prefilled_review.epa.desc)]
    form.implement_date.data = prefilled_review.implement_date
    form.review_compliment.data = prefilled_review.review_compliment
    form.review_suggestion.data = prefilled_review.review_suggestion
    if prefilled_review.review_difficulty:
        form.review_difficulty.data = str(prefilled_review.review_difficulty.id)
    if prefilled_review.review_score:
        form.review_score.data = str(prefilled_review.review_score.id)
    
    return render_template('make_review.html', title="填寫/編輯評核", form=form, review=prefilled_review, review_type="fill")

@login_required
def remove_review(review_id):
    try:
        review = Review.query.get(review_id)
    except Exception as e:
        flash('review not found!')
        print(e)

    if current_user.can_remove_review(review):
        try:
            db.session.delete(review)
            db.session.commit()
            flash('已成功刪除', 'alert-info')
        except Exception as e:
            flash('未成功刪除，如果問題一直存在，請聯絡管理員')
            print(e)
    return redirect(url_for('view_reviews'))    

@login_required
def view_reviews():
    sort_keys = request.args.get("sort_keys", "") # EPA, implement_date, create_time, complete
    sort_keys_list = sort_keys.split(",")
    sort_entity_list = []
    for key in sort_keys_list:
        if key == "EPA":
            sort_entity_list.append(Review.epa_id)
        elif key == "implement_date":
            sort_entity_list.append(Review.implement_date.desc())
        elif key == "create_time":
            sort_entity_list.append(Review.create_time.desc())
        elif key == "complete":
            sort_entity_list.append(Review.complete)
    if len(sort_keys_list) == 0:
        sort_entity_list.append(Review.complete)

    cur_page_num = int(request.args.get('page') or 1)
    all_user_related_reviews_q = Review.query.filter(or_(Review.reviewer==current_user, Review.reviewee==current_user))
    
    all_user_related_reviews_q = all_user_related_reviews_q.order_by(*sort_entity_list)
    all_user_related_reviews = all_user_related_reviews_q.paginate(page=cur_page_num, per_page=int(current_app.config['REVIEW_PER_PAGE']), error_out=False)
    next_url = url_for('view_reviews', page=all_user_related_reviews.next_num, sort_keys=sort_keys) if all_user_related_reviews.has_next else None
    prev_url = url_for('view_reviews', page=all_user_related_reviews.prev_num, sort_keys=sort_keys) if all_user_related_reviews.has_prev else None
    return render_template('view_reviews.html', title="查看所有評核", reviews=all_user_related_reviews.items, next_url=next_url, prev_url=prev_url)

@login_required
def new_review():
    prefilled_review = Review()
    # (1) form configuration
    form = ReviewForm()
    form.epa.choices = [(epa.id, epa.desc) for epa in EPA.query.all()]
    form.location.choices = [(location.id, location.desc) for location in Location.query.all()]

    user_options = list(set(current_user.internal_group.internal_users.all() + current_user.internal_group.external_users))
    form.reviewee.choices = [(user.id, user.username) for user in user_options if user!=current_user]
    form.reviewer.choices = [(current_user.id, current_user.username)]

    form.review_difficulty.choices = [(review_difficulty.id, review_difficulty.desc) for review_difficulty in ReviewDifficulty.query.all()]
    form.review_score.choices = [(review_score.id, review_score.desc) for review_score in ReviewScore.query.all()]
    # (2) on submit handling
    if form.validate_on_submit():
        review = Review()
        review.implement_date = form.implement_date.data
        review.epa = EPA.query.get(form.epa.data)
        review.location = Location.query.get(int(form.location.data))
        review.reviewee = User.query.get(form.reviewee.data)
        review.reviewer = current_user
        review.review_score = ReviewScore.query.get(int(form.review_score.data))
        review.review_compliment = form.review_compliment.data
        review.review_suggestion = form.review_suggestion.data
        review.review_difficulty = ReviewDifficulty.query.get(int(form.review_difficulty.data))
        review.review_source = ReviewSource.query.filter(ReviewSource.name=="new").first()
        review.last_edited = datetime.datetime.now()
        review.complete = True
        db.session.add(review)
        db.session.commit()

        subject = "[EPA通知]您已被評核"
        msg_body = f'{review.reviewee.username}你好，\n{review.reviewer.username}已評核你於{review.implement_date.strftime("%Y-%m-%d")}實作的{review.epa.desc}，你可前往系統查看'
        try:
            review.reviewee.send_message(subject=subject, msg_body=msg_body)
        except Exception as e:
            print(e)
        return redirect(url_for('index'))
        
    return render_template('make_review.html', title="新增評核", form=form, review=prefilled_review, review_type="new")

@login_required
def request_review():
    # anyone could make a review request to any teacher
    # fill epa, location, reviewer
    form = ReviewForm()
    form.reviewee.render_kw = {'disabled': 'disabled'}
    form.reviewee.choices = [("", current_user.username)]
    form.epa.choices = [(epa.id, epa.desc) for epa in EPA.query.all()]
    form.location.choices = [(location.id, location.desc) for location in Location.query.all()]

    current_user_groups = set(current_user.external_groups.all() + [current_user.internal_group])
    form.reviewer.choices = list(set([(user.id, user.username) for group in current_user_groups for user in group.internal_users if user != current_user and user.role.can_create_and_edit_review]))
    
    if form.is_submitted():
        review = Review()
        review.epa = EPA.query.get(form.epa.data)
        review.location = Location.query.get(form.location.data)
        review.implement_date = form.implement_date.data
        review.reviewee = current_user
        review.reviewer = User.query.get(form.reviewer.data)
        review.review_source = ReviewSource.query.filter(ReviewSource.name=="request").first()
        review.complete = False
        db.session.add(review)
        db.session.commit()

        flash(f'提交成功，已透過 Line 或 email 通知 {review.reviewer.username} 評核', "alert-success")
        subject = f"[EPA通知]請評核{review.reviewee.username}"
        msg_body = f"{review.reviewer.username}你好，\n{review.reviewee.username}請求您評核他於{review.implement_date}實作的{review.epa.desc}，你可前往系統填寫"
        try:
            review.reviewer.send_message(subject, msg_body)
        except Exception as e:
            print(e)

        return redirect(url_for('index'))
    return render_template('make_review.html', title="請求評核", form=form, review_type="request")



@login_required
def index():
    unfin_being_reviews = current_user.being_reviews.filter(Review.complete==False).all()
    unfin_make_reviews = current_user.make_reviews.filter(Review.complete==False).all()
    return render_template(
        'index.html', title="首頁", unfin_being_reviews=unfin_being_reviews, unfin_make_reviews=unfin_make_reviews
    )

def login_token():
    login_token = request.args.get("login_token", None)
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_jwt(login_token)
    if not user:
        flash('連結已過期，請以帳號密碼登入，或透過Line對話筐重新索取登入連結')
        return redirect(url_for('login'))
    login_user(user)
    return redirect(url_for('index'))

def login():
    # already login
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            flash('帳號或密碼錯誤', 'alert-danger')
            return redirect(url_for('login'))
        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html', title="登入", form=form)

def logout():
    logout_user()
    return redirect(url_for('login'))


def register():
    line_new_user_token = request.args.get("line_new_user_token", None)
    if line_new_user_token:
        try:
            line_new_user = LineNewUser.verify_jwt(line_new_user_token)
            line_user_profile = line_bot_api.get_profile(line_new_user.line_userId)
        except Exception as e:
            flash('抱歉，無法辨識你的 Line 帳號，你還是可以繼續註冊，或退出後再次聯繫EPA Line官方帳號索取註冊連結', 'alert-warning')
            print(e)
            line_user_profile = None
    else:
        line_user_profile = None

    if current_user.is_authenticated:
        if not current_user.line_userId:
            if line_user_profile:
                current_user.line_userId = line_new_user.line_userId
                db.session.commit()
                flash('已將你的帳號與line帳號綁定', 'alert-success')
                return redirect(url_for('index'))
            else:
                flash('綁定失敗，你的line帳號似乎出了點問題，請聯絡系統管理者','alert-danger')
        return redirect(url_for('index'))
    # (1) form configuration
    form = RegisterForm()
    registerable_roles = Role.query.filter(Role.is_manager == False).with_entities(Role.id, Role.name).all()
    form.role.choices = [(role.id.hex, role.name) for role in registerable_roles]
    form.bindline.data = True if line_user_profile else False
    all_groups = Group.query.all()
    form.internal_group.choices = [(group.id.hex, group.name) for group in all_groups]
    form.external_groups.choices = [(group.id.hex, group.name) for group in all_groups]

    # (2) on submit handling
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.role = Role.query.filter(Role.id == form.role.data, Role.is_manager == False ).first()
        if line_user_profile and form.bindline.data:
            user.line_userId = line_user_profile.user_id
            db.session.delete(line_new_user)
        user.internal_group = Group.query.get(form.internal_group.data)
        
        for group_id in form.external_groups.data:
            user.external_groups.append(Group.query.get(group_id))

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(Markup('註冊成功，請以帳號密碼登入<br>如果你有綁定Line帳號，歡迎透過 <a href="https://line.me/R/ti/p/{{linebotinfo.basic_id}}">Line官方帳號</a>使用快速登入功能'), 'alert-success')
        return redirect(url_for('login'))
    
    if not line_user_profile:
        flash(Markup('EPA系統可以透過 line 通知你，你可以考慮 <a href="https://line.me/R/ti/p/{{linebotinfo.basic_id}}">點此透過line註冊</a>'), 'alert-info')
    linebotinfo = line_bot_api.get_bot_info()
    return render_template('register.html', title='註冊新帳號', form=form, line_user_profile=line_user_profile, linebotinfo=linebotinfo)

@login_required
def user(username):
    if current_user.role.is_manager:
        flash("This is a page accessable for 醫院管理者. If you think this is an error, Please contact to get access",'alert-danger')
        return redirect(url_for('index'))
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    current_page_num = int(request.args.get('page') or 1)
    all_user_related_reviews = Review.query.filter(or_(Review.reviewer==current_user, Review.reviewee==current_user)).order_by(Review.last_edited.desc())\
                    .paginate(page=cur_page_num, per_page=int(current_app.config['REVIEW_PER_PAGE']), error_out=False)
    next_url = url_for('user',page=all_user_related_reviews.next_num) if all_user_related_reviews.has_next else None
    prev_url = url_for('user', page=all_user_related_reviews.prev_num) if all_user_related_reviews.has_prev else None
    
    if request.method == 'POST':
        if request.form['request_button'] == 'Follow':
            current_user.follow(u)
            db.session.commit()
        elif request.form['request_button'] == "Unfollow":
            current_user.unfollow(u)
            db.session.commit()
        else:
            flash("Send an email to your email address, please check!!!!",'alert-info')
            send_email_for_user_activate(current_user)
    return render_template(
        'user.html',
        title='Profile',
        tweets=tweets.items,
        user=u,
        next_url=next_url,
        prev_url=prev_url
    )

def send_email_for_user_activate(user):

    token = user.get_jwt()
    url_user_activate = url_for(
        'user_activate',
        token=token,
        _external=True # external make the url universaly aviable
    )
    send_email(
        subject=current_app.config['MAIN_SUBJECT_USER_ACTIVATE'],
        recipients=[user.email],
        text_body= render_template(
            'email/user_activate.txt',
            username=user.username,
            url_user_activate=url_user_activate
        ),
        html_body=render_template(
            'email/user_activate.html',
            username=user.username,
            url_user_activate=url_user_activate
        )
    )

def user_activate(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        msg = "Token has expired, please try to re-send email"
    else:
        user.is_activated = True
        db.session.commit()
        msg = 'User has been activated!'
    return render_template(
        'user_activate.html', msg=msg
    )


def page_not_found(e):
    return render_template('404.html'), 404


@login_required
def edit_profile():
    print("in edit_profile()")
    linebotinfo = line_bot_api.get_bot_info()
    if current_user.line_userId:
        try:
            line_user_profile = line_bot_api.get_profile(current_user.line_userId)
        except Exception as e:
            print(e)
    else:
        print("no line_userId")
        line_user_profile = None
    
    # (1) form configuration
    form = EditProfileForm()
    all_groups = Group.query.with_entities(Group.id, Group.name).all()
    form.role.render_kw = {'disabled': 'disabled'}
    form.internal_group.choices = [(group.id.hex, group.name) for group in all_groups]
    form.external_groups.choices = [(group.id.hex, group.name) for group in all_groups]

    # (2) on submit handling
    if form.validate_on_submit():
        if not form.bindline.data:
            current_user.line_userId = None
        current_user.email = form.email.data
        current_user.internal_group = Group.query.get(form.internal_group.data)
        current_user.external_groups = [Group.query.get(group_id) for group_id in form.external_groups.data]
        db.session.commit()
        flash('資料更新成功','alert-success')
        return redirect(url_for('edit_profile'))
    # (3) prefill
    form.bindline.data = True if current_user.line_userId else False
    form.email.data = current_user.email
    form.role.choices = [("", current_user.role.name)] # for dummy field, make sure you have default choice in form class definition
    form.internal_group.data = current_user.internal_group.id.hex
    form.external_groups.data = [ext_group.id.hex for ext_group in current_user.external_groups]
    
    return render_template('edit_profile.html',title=current_user.username, form=form, linebotinfo=linebotinfo, line_user_profile=line_user_profile)


def reset_password_request():
    # if already login, directly reset
    if current_user.is_authenticated:
        token = current_user.get_jwt()
        return redirect(url_for('password_reset',token=token))

    form = PasswdResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("已發送密碼重置連結到你的 line 或 email", 'alert-info')
            token = user.get_jwt()
            url_password_reset = url_for('password_reset',token=token,_external=True)
            subject = "[EPA]密碼重設"
            msg_body = f'{user.username}你好，\n你的密碼重設連結為{url_password_reset}'
            try:
                user.send_message(subject, msg_body)
            except Exception as e:
                print(e)
        else:
            flash('找不到這個這個email註冊的使用者', 'alert-warning')
        return redirect(url_for('login'))
    return render_template('password_reset_request.html', form=form)


def password_reset(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        flash('你哪來這個 Token  是我給的嗎？','alert-info')
        return redirect(url_for('login'))
    form = PasswdResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('密碼重設完成，記得下次用新密碼登入喔！','alert-info')
        subject = "[EPA通知]密碼已重設"
        msg_body = f'{user.username}你好，你的EPA密碼已重設，如果您並未發出重設密碼請求，請立即聯絡管理員'
        user.send_message()
        return redirect(url_for('login'))
    return render_template(
        'password_reset.html', title='Password Reset', form=form
    )


def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # if registered, reply login link(using token)
    print(f"event type: {event.type}")
    line_userId = event.source.user_id # The attribute is called user_id, surprise lol
    print(line_userId)
    
    user = User.query.filter(User.line_userId == line_userId).first()
    
    if not user:
        # I think this is not safe. But let use this for now
        # for more advanced link token see, https://developers.line.biz/en/docs/messaging-api/linking-accounts/#implement-account-link-feature
        # or alternatively, we could have our own token auth method
        line_new_user = LineNewUser(line_userId=line_userId)
        db.session.add(line_new_user)
        db.session.commit()
        line_new_user_token = line_new_user.get_jwt()
        app_webhook = current_app.config['WEBHOOK_URL']
        line_bot_api.reply_message(event.reply_token,TextSendMessage(f'新用戶你好，請點此連結註冊: {app_webhook}/register?line_new_user_token={line_new_user_token}'))  
    else:
        # if registered, issue a login URL with token
        login_token = user.get_jwt()
        url_index = url_for('login_token',login_token=login_token, _external=True)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(f'嗨，{user.username}，請點此連結進入EPA系統 {url_index}'))  

    