from datetime import datetime

from twittor import db
from twittor.models.fact import EPA, Location


class Review(db.Model):
    __table__name = "review"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Integer, db.ForeignKey('location.id'))
    epa = db.Column(db.Integer, db.ForeignKey('epa.id'))
    reviewee_id = db.Column(db.Integer, db.ForeignKey('reviewee.id')) 
    reviewer_id = db.Column(db.Integer, db.ForeignKey('reviewer.id')) 
    review_difficulty = db.Column(db.Integer) 
    review_compliment = db.Column(db.String(512))
    review_suggestion = db.Column(db.String(512))
    review_score = db.Column(db.Integer)
    complete = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_edited = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"review:  id={self.id}, requester={self.requester}, reviewer={self.reviewer}, location={self.location}, epa={self.epa}, create_time={self.create_time}"
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "id={}, body={}, create_time={}, user_id={}".format(
            self.id, self.body, self.create_time, self.user_id
        )