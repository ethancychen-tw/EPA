from datetime import datetime

from twittor import db


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "id={}, body={}, create_time={}, user_id={}".format(
            self.id, self.body, self.create_time, self.user_id
        )


class AskReview(db.Model):
    __tablename__ = 'ask_review'
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.String(30))  # later make these foreign keys
    reviewer = db.Column(db.String(30))  # later make these foreign keys
    location = db.Column(db.String(30))  # later make these foreign keys
    epa = db.Column(db.String(30))  # later make these foreign keys
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"id={self.id}, requester={self.requester}, reviewer={self.reviewer}, location={self.location}, epa={self.epa}, create_time={self.create_time}"