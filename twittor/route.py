from flask import render_template, redirect, url_for, request, \
    abort, current_app, flash
from flask_login import login_user, current_user, logout_user, login_required

from twittor.forms import LoginForm, RegisterForm, EditProfileForm, TweetForm, \
    PasswdResetRequestForm, PasswdResetForm, AskReviewForm, ReviewForm
from twittor.models.user import User, load_user, EPA, Location, Reviewee, Reviewer
from twittor.models.tweet import Tweet, Review
from twittor import db
from twittor.email import send_email

def review():
    # form.field(disabled=True)

    form = ReviewForm()
    try:
        ask_review_id = request.args.get("ask_review_id", None)

        ask_review_id = 1
        if not ask_review_id:
            raise ValueError("not from ask review")
        
        print(ask_review_id)
        print(AskReview.query.get(int(ask_review_id)))
        ask_review = AskReview.query.get(int(ask_review_id))
        # TODO auth for this user. If not, raise error
        prefilled_location = Location.query.with_entities(Location.id, Location.name, Location.desc).get(ask_review.location)
        prefilled_epa = EPA.query.with_entities(EPA.id, EPA.title, EPA.desc).get(ask_review.epa)
        prefilled_reviewee = User.query.get(ask_review.requester)
        
        # Question: is it ok that I reveal primary key?
        form.location.choices = [(prefilled_location.id, prefilled_location.name)]
        form.epa.choices = [(prefilled_epa.id, prefilled_epa.title) ]
        form.reviewee.choices = [(prefilled_reviewee.id, prefilled_reviewee.username)]  

    except:
        form.location.choices = [(location.id, location.name) for location in Location.query.with_entities(Location.id, Location.name).all()]
        form.epa.choices = [(epa.id, epa.title) for epa in EPA.query.with_entities(EPA.id, EPA.title).all()]
        # Question: is it ok that I reveal primary key?
        form.reviewee.choices = [(user.id, user.username) for user in User.query.with_entities(User.username, User.id)]  
    
    # TODO should fill in the (logined) reviewer user
    user = User.query.with_entities(User.id, User.username).first()
    if not user:
        return redirect('/index')
    form.reviewer.choices = [(user.id, user.username)]


    
    # form.location.choices = [(location.desc, location.name) for location in Location.query.with_entities(Location.name, Location.desc)]
    # form.epa.choices = [(epa.desc, epa.title) for epa in EPA.query.with_entities(EPA.title, EPA.desc).all()]
    # # Question: is it ok that I reveal primary key?
    # form.reviewer.choices = [(user.id, user.username) for user in User.query.with_entities(User.username, User.id)]  
    # form.requester.choices = [(user.id, user.username) for user in User.query.with_entities(User.username, User.id)]

    # if form.validate_on_submit():
    #     ar = AskReview(
    #             location=form.location.data,
    #             epa=form.epa.data,
    #             requester=form.requester.data,
    #             reviewer=form.reviewer.data
    #         )
    #     db.session.add(ar)
    #     db.session.commit()
    #     return redirect(url_for('index'))
    return render_template('review.html', form=form)

def ask_review():
    form = AskReviewForm()

    form.location.choices = [(location.id, location.name) for location in Location.query.with_entities(Location.id, Location.name)]
    form.epa.choices = [(epa.id, epa.name) for epa in EPA.query.with_entities(EPA.id, EPA.name).all()]
    # Question: is it ok that I reveal primary key?
    form.reviewer.choices = [(reviwer.id, reviwer.username) for reviwer in Reviewer.query.join(User).with_entities(User.username, Reviewer.id).all()]  
    # reviewee should be login user
    reviewee = Reviewee.query.join(User).filter(User.id==current_user.id).with_entities(Reviewee.id, User.username).first()
    form.requester.choices = [(reviewee.id, reviewee.username)]
    

    if form.validate_on_submit():
        review = Review(
                location=form.location.data,
                epa=form.epa.data,
                Reviewee=Reviewee.query.get(form.reviewee.data),
                reviewer=form.reviewer.data
            )
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('ask_review.html', form=form)


@login_required
def index():
    form = TweetForm()
    if form.validate_on_submit():
        t = Tweet(body=form.tweet.data, author=current_user)
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('index'))
    page_num = int(request.args.get('page') or 1)
    tweets = current_user.own_and_followed_tweets().paginate(
        page=page_num, per_page=current_app.config['TWEET_PER_PAGE'], error_out=False)

    next_url = url_for('index', page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for('index', page=tweets.prev_num) if tweets.has_prev else None
    return render_template(
        'index.html', tweets=tweets.items, form=form, next_url=next_url, prev_url=prev_url
    )


def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # for now, direct login 
    user = User.query.first()
    login_user(user)
    flash(' direct login as user1 for now', 'error')
    return redirect(url_for('index'))
    # if form.validate_on_submit():
    #     u = User.query.filter_by(username=form.username.data).first()
    #     if u is None or not u.check_password(form.password.data):
    #         flash('invalid username or password')
    #         return redirect(url_for('login'))
    #     login_user(u, remember=form.remember_me.data)
    #     next_page = request.args.get('next')
    #     if next_page:
    #         return redirect(next_page)
    #     return redirect(url_for('index'))
    return render_template('login.html', title="Sign In", form=form)

def logout():
    logout_user()
    return redirect(url_for('login'))


def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)

@login_required
def user(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    page_num = int(request.args.get('page') or 1)
    tweets = u.tweets.order_by(Tweet.create_time.desc()).paginate(
        page=page_num,
        per_page=current_app.config['TWEET_PER_PAGE'],
        error_out=False)

    next_url = url_for(
        'profile',
        page=tweets.next_num,
        username=username) if tweets.has_next else None
    prev_url = url_for(
        'profile',
        page=tweets.prev_num,
        username=username) if tweets.has_prev else None
    if request.method == 'POST':
        if request.form['request_button'] == 'Follow':
            current_user.follow(u)
            db.session.commit()
        elif request.form['request_button'] == "Unfollow":
            current_user.unfollow(u)
            db.session.commit()
        else:
            flash("Send an email to your email address, please check!!!!")
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
        _external=True
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
    form = EditProfileForm()
    if request.method == 'GET':
        form.about_me.data = current_user.about_me
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    return render_template('edit_profile.html', form=form)


def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswdResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(
                "You should soon receive an email allowing you to reset your \
                password. Please make sure to check your spam and trash \
                if you can't find the email."
            )
            token = user.get_jwt()
            url_password_reset = url_for(
                'password_reset',
                token=token,
                _external=True
            )
            url_password_reset_request = url_for(
                'reset_password_request',
                _external=True
            )
            send_email(
                subject=current_app.config['MAIL_SUBJECT_RESET_PASSWORD'],
                recipients=[user.email],
                text_body= render_template(
                    'email/passwd_reset.txt',
                    url_password_reset=url_password_reset,
                    url_password_reset_request=url_password_reset_request
                ),
                html_body=render_template(
                    'email/passwd_reset.html',
                    url_password_reset=url_password_reset,
                    url_password_reset_request=url_password_reset_request
                )
            )
        return redirect(url_for('login'))
    return render_template('password_reset_request.html', form=form)


def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        return redirect(url_for('login'))
    form = PasswdResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template(
        'password_reset.html', title='Password Reset', form=form
    )


@login_required
def explore():
    # get all user and sort by followers
    page_num = int(request.args.get('page') or 1)
    tweets = Tweet.query.order_by(Tweet.create_time.desc()).paginate(
        page=page_num, per_page=current_app.config['TWEET_PER_PAGE'], error_out=False)

    next_url = url_for('index', page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for('index', page=tweets.prev_num) if tweets.has_prev else None
    return render_template(
        'explore.html', tweets=tweets.items, next_url=next_url, prev_url=prev_url
    )