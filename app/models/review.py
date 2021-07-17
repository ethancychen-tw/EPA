from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
import uuid
from app import db

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  
    creator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id')) 
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    epa_id = db.Column(db.Integer, db.ForeignKey('epa.id'))
    implement_date = db.Column(db.DateTime)
    review_source_id = db.Column(db.Integer, db.ForeignKey('review_source.id'))
    review_difficulty_id = db.Column(db.Integer, db.ForeignKey('review_difficulty.id')) 
    review_score_id = db.Column(db.Integer, db.ForeignKey('review_score.id')) 
    reviewee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id')) 
    reviewee_note = db.Column(db.String(512))
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    review_compliment = db.Column(db.String(512))
    review_suggestion = db.Column(db.String(512))
    is_draft = db.Column(db.Boolean, default=True)
    complete = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    last_edited = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"""review:  
        id={self.id}, 
        review_source_id={self.review_source_id},
        reviewee_id={self.reviewee_id}, 
        reviewer_id={self.reviewer_id}, 
        location={self.location_id}, 
        epa={self.epa_id}, 
        create_time={self.create_time}, 
        review_source_id{self.review_score_id}, 
        review_difficulty_id={self.review_difficulty_id}
        """
    
    # 一旦 complete，draft 就會自動變成 False
    @validates('status_complete')
    def validate_status_complete(self, key, field):
        if field:
            self.status_draft = False
        return field

    @validates('status_draft')
    def validate_status_draft(self, key, field):
        if field:
            assert not self.status_complete
        return field

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

    reviews = db.relationship('Review', backref='location', lazy='dynamic')
    def __repr__(self):
        return f"location: id={self.id}, name={self.name},desc={self.desc}"

class MilestoneItemEPA(db.Model):
    # see association object example in here:
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
    __tablename__ = 'milestone_item_epa'
    milestoneitem_id = db.Column(db.Integer, db.ForeignKey('milestone_item.id'), primary_key=True)
    epa_id = db.Column(db.Integer, db.ForeignKey('epa.id'), primary_key=True)
    min_epa_level = db.Column(db.Integer)
    epa = db.relationship("EPA", back_populates="milestone_items")
    milestone_item = db.relationship("MilestoneItem", back_populates="epas")
class EPA(db.Model):
    __tablename__ = 'epa'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    reviews = db.relationship('Review', backref='epa', lazy='dynamic')
    milestone_items = db.relationship('MilestoneItemEPA', back_populates="epa")

class MilestoneItem(db.Model):
    __tablename__ = 'milestone_item'
    id = db.Column(db.Integer, primary_key=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'))
    code = db.Column(db.String(16)) # E.g. PC1.1.1
    level = db.Column(db.Integer)
    content = db.Column(db.String(256))
    epas = db.relationship("MilestoneItemEPA", back_populates="milestone_item")
    milestone = db.relationship("Milestone", backref="milestone_items")

class Milestone(db.Model):
    __tablename__ = 'milestone'
    id = db.Column(db.Integer, primary_key=True)
    corecompetence_id = db.Column(db.Integer, db.ForeignKey('corecompetence.id'))
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

class CoreCompetence(db.Model):
    __tablename__  = 'corecompetence'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    milestones = db.relationship('Milestone', backref='corecompetence', lazy='dynamic')
    


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
    