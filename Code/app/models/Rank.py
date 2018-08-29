from app import db


class Rank(db.Model):
    __tablename__ = 'rank'
    place_id = db.Column(db.String(50), db.ForeignKey('school.place_id'), primary_key=True)
    name = db.Column(db.String(255), nullable=False, primary_key=True)
    official_school_name = db.Column(db.String(255))
    rank = db.Column(db.Integer)
    p_rank = db.Column(db.Integer)
    gender_type = db.Column(db.String(50))
    at_university = db.Column(db.Float(10))  # ?
    at_third_level = db.Column(db.Float)
    boy = db.Column(db.Integer)
    girl = db.Column(db.Integer)
    stu_tea_ratio = db.Column(db.Float(10))  # ?
    photo = db.Column(db.String(255))
