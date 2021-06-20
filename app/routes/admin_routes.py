from flask import (
    render_template,
    redirect,
    url_for,
    request,
    abort,
    current_app,
    flash,
    Markup,
)
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models.review import Review
from app.models.user import User, Notification

@login_required
def admin_view_users():
    pass

@login_required
def user(username):
    if current_user.role.is_manager:
        flash(
            "This is a page accessable for 醫院管理者. If you think this is an error, Please contact to get access",
            "alert-danger",
        )
        return redirect(url_for("index"))
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    current_page_num = int(request.args.get("page") or 1)
    all_user_related_reviews = (
        Review.query.filter(
            or_(Review.reviewer == current_user, Review.reviewee == current_user)
        )
        .order_by(Review.last_edited.desc())
        .paginate(
            page=current_page_num,
            per_page=int(current_app.config["REVIEW_PER_PAGE"]),
            error_out=False,
        )
    )
    next_url = (
        url_for("user", page=all_user_related_reviews.next_num)
        if all_user_related_reviews.has_next
        else None
    )
    prev_url = (
        url_for("user", page=all_user_related_reviews.prev_num)
        if all_user_related_reviews.has_prev
        else None
    )

    if request.method == "POST":
        if request.form["request_button"] == "Follow":
            current_user.follow(u)
            db.session.commit()
        elif request.form["request_button"] == "Unfollow":
            current_user.unfollow(u)
            db.session.commit()
        else:
            flash("Send an email to your email address, please check!!!!", "alert-info")
            send_email_for_user_activate(current_user)
    return render_template(
        "user.html",
        title="Profile",
        tweets=tweets.items,
        user=u,
        next_url=next_url,
        prev_url=prev_url,
    )

@login_required
def create_notifications_fill_review_wrapper():
    if current_user.role.is_manager:
        create_notifications_fill_review()
    else:
        return False

def create_notifications_fill_review(flush=False):
    unfin_reviews = Review.query.filter(Review.complete == False).all()
    for review in unfin_reviews:
        # could refactor with request_review msg
        subject = f"[EPA通知]請評核{review.reviewee.username}"
        msg_body = f'{review.reviewer.username}你好，\n{review.reviewee.username}請求您評核他於{review.implement_date}實作的{review.epa.desc}，你可點此<a href="{url_for("inspect_review",review_id=review.id,_external=True)}">查看</a>'
        notification = Notification(user_id=review.reviewer.id, subject=subject, msg_body=msg_body)
        db.session.add(notification)
    db.session.commit()
    if flush:
        flush_notifications()

def flush_notifications():
    notifications = Notification.query.all()
    