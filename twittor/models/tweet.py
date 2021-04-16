from datetime import datetime

from twittor import db
from twittor.models.fact import EPA, Location


class Review(db.Model):
    __table__name = "review"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    epa_id = db.Column(db.Integer, db.ForeignKey('epa.id'))
    review_source_id = db.Column(db.Integer, db.ForeignKey('review_source.id'))
    review_difficulty_id = db.Column(db.Integer, db.ForeignKey('review_difficulty.id')) 
    review_score_id = db.Column(db.Integer, db.ForeignKey('review_score.id')) 
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_compliment = db.Column(db.String(512))
    review_suggestion = db.Column(db.String(512))
    complete = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_edited = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"""review:  
        id={self.id}, 
        review_source_id={self.review_source_id},
        reviewee_id={self.reviewee_id}, 
        reviewer_id={self.reviewer_id}, 
        location={self.location_id}, 
        epa={self.epa_id}, 
        create_time={self.create_time}, 
        review_source_id={self.review_score_id}, 
        review_difficulty_id={self.review_difficulty_id}
        """
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "id={}, body={}, create_time={}, user_id={}".format(
            self.id, self.body, self.create_time, self.user_id
        )