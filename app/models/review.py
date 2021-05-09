from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app import db
class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    epa_id = db.Column(db.Integer, db.ForeignKey('epa.id'))
    implement_date = db.Column(db.DateTime)
    review_source_id = db.Column(db.Integer, db.ForeignKey('review_source.id'))
    review_difficulty_id = db.Column(db.Integer, db.ForeignKey('review_difficulty.id')) 
    review_score_id = db.Column(db.Integer, db.ForeignKey('review_score.id')) 
    reviewee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id')) 
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    review_compliment = db.Column(db.String(512))
    review_suggestion = db.Column(db.String(512))
    complete = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    last_edited = db.Column(db.DateTime)

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

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

    reviews = db.relationship('Review', backref='location', lazy='dynamic')
    def __repr__(self):
        return f"location: id={self.id}, name={self.name},desc={self.desc}"

class EPA(db.Model):
    __tablename__ = 'epa'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

    reviews = db.relationship('Review', backref='epa', lazy='dynamic')
    def __repr__(self):
        return f"epa: id={self.id}, name={self.name},desc={self.desc}"

class ReviewScore(db.Model):
    __tablename__ = 'review_score'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    
    reviews = db.relationship('Review', backref='review_score', lazy='dynamic')
    def __repr__(self):
        return f"review_score: id={self.id}, value={self.value},  name={self.name},desc={self.desc}"

class ReviewDifficulty(db.Model):
    __tablename__ = 'review_difficulty'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

    review = db.relationship('Review', backref='review_difficulty', lazy='dynamic')
    def __repr__(self):
        return f"review_difficulty: id={self.id}, value={self.value},  name={self.name},desc={self.desc}"

class ReviewSource(db.Model):
    __tablename__ = 'review_source'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))  

    review = db.relationship('Review', backref='review_source', lazy='dynamic')
    def __repr__(self):
        return f"review_source: id={self.id}, name={self.name},desc={self.desc}"
    