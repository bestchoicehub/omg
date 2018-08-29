from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from datetime import datetime
from .Permission import Permission
from .User_operation import Compare, Follow, Comment
from .Roleomg import Role
import socket
import urllib.parse
import urllib.request
import simplejson



class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(50), unique=True, index=True, nullable=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)  # refigister time
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # last seen
    location = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    facebook_id = db.Column(db.String(50))
    photo = db.Column(db.String(256))
    # real_avatar = db.Column(db.String(128), default=None)
    login_type = db.Column(db.String(50))
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all,delete-orphan')
    compared = db.relationship('Compare', foreign_keys=[Compare.comparator_id],
                               backref=db.backref('comparator', lazy='joined'),
                               lazy='dynamic', cascade='all,delete-orphan')
    comments = db.relationship('Comment', backref=db.backref('author', lazy='joined'), lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)  # initial
        if self.login_type == 'website':
            if self.role is None:
                if self.email == current_app.config['FLASKY_ADMIN']:  #
                    self.role = Role.query.filter_by(name='Administrator').first()  # admin
                else:
                    self.role = Role.query.filter_by(default=True).first()  # default user

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # password function
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # confirm account
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # anonymous user
    @staticmethod
    def create_anonymous():
        device_name = socket.getfqdn(socket.gethostname())
        username = device_name
        email = device_name
        new_anonymous = User(username=username, email=email)
        db.session.add(new_anonymous)
        db.session.commit()

    @staticmethod
    def current_anonymous_user():
        device_name = socket.getfqdn(socket.gethostname())
        current_anonymous_user = User.query.filter_by(username=device_name).first()
        return current_anonymous_user

    # follow function
    def follow(self, school):
        if not self.is_following(school):
            f = Follow(follower_id=self.id, followed_id=school.place_id)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, school):
        f = self.followed.filter_by(followed_id=school.place_id).first()
        if f is not None:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, school):
        return self.followed.filter_by(followed_id=school.place_id).first() is not None

    # comparison function
    def comparison(self, school):
        if not self.is_comparing(school):
            comparision = Compare(comparator_id=self.id, compared_id=school.place_id)
        db.session.add(comparision)
        db.session.commit()

    def remove_comparison(self, school):
        removal = self.compared.filter_by(compared_id=school.place_id).first()
        if removal is not None:
            db.session.delete(removal)
            db.session.commit()

    def is_comparing(self, school):
        return self.compared.filter_by(compared_id=school.place_id).first() is not None

    # comment function
    def remove_comment(self, school):
        remove_comment = self.comments.filter_by(school_id=school.place_id).first()
        print(remove_comment)
        if remove_comment is not None:
            db.session.delete(remove_comment)
            db.session.commit()

    def has_commented(self, school):
        return self.comments.filter_by(school_id=school.place_id).first() is not None

    @staticmethod
    def get_coordination(query, from_sensor=False):
        geo_list = []
        # if 'ireland' not in query:
        #     query = query + " " + "Ireland"
        params = {
            'address': query,
            'sensor': "true" if from_sensor else "false",
            'key':"AIzaSyBuvPcSplTFiZEc0eKSutMEGrQf_LeIIyY"
        }
        print(urllib.parse.urlencode(params))
        url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.parse.urlencode(params)
        json_response = urllib.request.urlopen(url)
        response = simplejson.loads(json_response.read())
        if response['results']:
            location = response['results'][0]['geometry']['location']
            latitude, longitude = location['lat'], location['lng']
            geo_list.append(latitude)
            geo_list.append(longitude)
            print(query, latitude, longitude)
        else:
            print(query, "<no results>")
        return geo_list

    @staticmethod
    def get_city(lat, lon):
        url = "https://maps.googleapis.com/maps/api/geocode/json?"
        url += "latlng=%s,%s&sensor=false" % (lat, lon)
        url += "&key=AIzaSyBuvPcSplTFiZEc0eKSutMEGrQf_LeIIyY"
        json_response = urllib.request.urlopen(url).read()
        response = simplejson.loads(json_response)
        if response['results']:
            print("success")
            components = response['results'][0]['address_components']
            city = ''
            for c in components:
                if "County" in c['long_name']:
                    city = c['long_name'].replace("County ", "")

            if city == '':
                city = 'unknown'
        else:
            print("<no result>")
            city = 'unknown'
        return city

class Anonymous(AnonymousUserMixin):

    def can(self, permission):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
