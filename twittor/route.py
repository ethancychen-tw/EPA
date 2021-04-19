from flask import render_template, redirect, url_for, request, \
    abort, current_app, flash
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
from twittor.forms import LoginForm, RegisterForm, EditProfileForm, TweetForm, \
    PasswdResetRequestForm, PasswdResetForm, ReviewForm
from twittor.models.user import User, load_user
from twittor.models.tweet import Tweet, Review
from twittor.models.fact import EPA, Location, ReviewDifficulty, ReviewScore, ReviewSource
from twittor import db
from twittor.email import send_email

@login_required
def review(review_id):
    review = Review.query.get(review_id)
    if current_user != review.reviewer and current_user != review.reviewee:
        return redirect(url_for('index'))
    return render_template('review.html', review=review)

@login_required
def view_reviews():
    all_reviews = Review.query.filter(or_(Review.reviewer==current_user, Review.reviewee==current_user)).order_by(Review.last_edited.desc()).all()
    return render_template('view_reviews.html', reviews=all_reviews) #TODO pagingate

@login_required
def new_review():
    # teacher make review
    # fill all the blanks

    form = ReviewForm()
    
    form.epa.choices = [(epa.id, epa.desc) for epa in EPA.query.all()]
    form.location.choices = [(location.id, location.desc) for location in Location.query.all()]

    current_user_groups = current_user.groups.all()
    form.reviewee.choices = list(set([(user.id, user.username) for group in current_user_groups for user in group.users if user.role=="student"]))
    
    form.review_difficulty.choices = [(review_difficulty.id, review_difficulty.desc) for review_difficulty in ReviewDifficulty.query.all()]
    form.review_score.choices = [(review_score.id, review_score.desc) for review_score in ReviewScore.query.all()]
    
    if form.is_submitted():
        review = Review()
        review.epa = EPA.query.get(form.epa.data)
        review.location = Location.query.get(form.location.data)
        review.reviewee = User.query.get(form.reviewee.data)
        review.reviewer = current_user
        review.review_compliment = form.review_compliment.data
        review.review_suggestion = form.review_suggestion.data
        review.review_difficulty = ReviewDifficulty.query.get(form.review_difficulty.data)
        review.review_score = ReviewScore.query.get(form.review_score.data)
        review.review_source = ReviewSource.query.filter(ReviewSource.name=="new").first()
        review.complete = True
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('make_review.html', form=form, review_type="new")

@login_required
def request_review():
    # anyone could make a review request to any teacher
    # fill epa, location, reviewer
    form = ReviewForm()
    
    form.epa.choices = [(epa.id, epa.desc) for epa in EPA.query.all()]
    form.location.choices = [(location.id, location.desc) for location in Location.query.all()]

    current_user_groups = current_user.groups.all()
    form.reviewer.choices = list(set([(user.id, user.username) for group in current_user_groups for user in group.users if user.role=="teacher"]))
    
    if form.is_submitted():
        review = Review()
        review.epa = EPA.query.get(form.epa.data)
        review.location = Location.query.get(form.location.data)
        review.reviewee = current_user
        review.reviewer = User.query.get(form.reviewer.data)
        review.review_source = ReviewSource.query.filter(ReviewSource.name=="request").first()
        review.complete = False
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('index'))
    
    
    return render_template('make_review.html', form=form, review_type="request")

@login_required
def fill_review(review_id):
    # teacher may finish the review request by any others
    # fill review_X stuffts
    prefilled_review = Review.query.get(review_id)
    if prefilled_review.reviewer.id != current_user.id or prefilled_review.complete:
        return redirect(url_for('index'))
    form = ReviewForm()
    form.reviewer.data = prefilled_review.reviewer.username
    form.reviewee.data = prefilled_review.reviewee.username
    form.location.data = prefilled_review.location.desc
    form.epa.data = prefilled_review.epa.desc
    form.review_compliment.data = prefilled_review.review_compliment
    form.review_suggestion.data = prefilled_review.review_suggestion
    if prefilled_review.review_difficulty:
        form.review_difficulty.data = prefilled_review.review_difficulty.id
    if prefilled_review.review_score:
        form.review_score.data = prefilled_review.review_score.id

    form.review_difficulty.choices = [(review_difficulty.id, review_difficulty.desc) for review_difficulty in ReviewDifficulty.query.all()]
    form.review_score.choices = [(review_score.id, review_score.desc) for review_score in ReviewScore.query.all()]
    
    if form.is_submitted():
        review = prefilled_review
        review.review_compliment = form.review_compliment.data
        review.review_suggestion = form.review_suggestion.data
        review.review_difficulty = ReviewDifficulty.query.get(form.review_difficulty.data)
        review.review_score = ReviewScore.query.get(form.review_score.data)
        review.complete = True
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('make_review.html', form=form, review_type="fill")

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
    # already login
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # for now, direct login 
    user = User.query.get(6)
    login_user(user)
    flash(' direct login for now', 'error')
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


# @login_required
# def explore():
#     # get all user and sort by followers
#     page_num = int(request.args.get('page') or 1)
#     tweets = Tweet.query.order_by(Tweet.create_time.desc()).paginate(
#         page=page_num, per_page=current_app.config['TWEET_PER_PAGE'], error_out=False)

#     next_url = url_for('index', page=tweets.next_num) if tweets.has_next else None
#     prev_url = url_for('index', page=tweets.prev_num) if tweets.has_prev else None
#     return render_template(
#         'explore.html', tweets=tweets.items, next_url=next_url, prev_url=prev_url
#     )