from app import db
from datetime import datetime


class Follow(db.Model):
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.String(50), db.ForeignKey('school.place_id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Compare(db.Model):
    __tablename__ = 'compare'
    comparator_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    compared_id = db.Column(db.String(50), db.ForeignKey('school.place_id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    _tablename_ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    commented_official_school_name = db.Column(db.String(255))
    author_avatar = db.Column(db.String(255))
    author_name = db.Column(db.String(50))
    user_rating = db.Column(db.Integer)
    user_review = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.now(), index=True)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    school_id = db.Column(db.String(50), db.ForeignKey('school.place_id'))

    @staticmethod
    def compute_overall_rate(rates):
        len1 = len(rates)
        if len1 == 0:
            len1 = 1
        overall_rate = sum(rates)/len1
        return overall_rate

# class History(db.Model):
#     _tablename_ = 'user_history'
#     history_id = db.Column(db.String(50), primary_key=True)
#     time = db.Column(db.DateTime, default=datetime.now())
#     user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'))
#     roll_number = db.Column(db.String(50), db.ForeignKey('school.roll_number'))
#
# class Write_comments(db.Model):
#     _tablename_ = 'write_comments'
#     w_id = db.Column(db.String(50), primary_key=True)
#     title = db.Column(db.Text, nullable=False)
#     time = db.Column(db.DateTime, default=datetime.now())
#     detail = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'))
#     comments = db.relationship('Comments', backref=db.backref('w_id1'), lazy='select')
#

