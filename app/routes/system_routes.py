# should refactor this into etl_


def inform_incomplete_reviews():
    reviewer_unfin_review_cnt_list = (
        Review.query.filter(Review.complete == False)
        .group_by(Review.reviewer_id)
        .with_entities(
            Review.reviewer_id, func.count(Review.id).label("unfin_review_cnt")
        )
        .all()
    )

    for reviewer_unfin_review_cnt in reviewer_unfin_review_cnt_list:
        try:
            # TODO: change to async send using Thread
            reviewer = User.query.get(reviewer_unfin_review_cnt.reviewer_id)
            subject = f"[EPA通知]尚未完成的評核"
            msg_body = f"{reviewer.username}你好，你尚有{reviewer_unfin_review_cnt.unfin_review_cnt}個評核未完成，你可前往系統填寫"
            reviewer_unfin_review_cnt.reviewer.send_message(
                subject=subject, msg_body=msg_body
            )
        except Exception as e:
            print(e)

# should refactor this into etl_
def auto_create_review():
    """
    find
    """