from twittor import db

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

    review = db.relationship('Review', backref='location', lazy='dynamic')
    def __repr__(self):
        return f"location: id={self.id}, name={self.name},desc={self.desc}"

class EPA(db.Model):
    __tablename__ = 'epa'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))

    review = db.relationship('Review', backref='epa', lazy='dynamic')
    def __repr__(self):
        return f"epa: id={self.id}, name={self.name},desc={self.desc}"

class ReviewScore(db.Model):
    __tablename__ = 'review_score'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    
    review = db.relationship('Review', backref='review_score', lazy='dynamic')
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
    