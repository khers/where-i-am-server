from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    locations = db.relationship('Location', backref='who', lazy='dynamic')
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    def to_json(self):
        json_user = {
                'id': self.id,
                'nickname': self.nickname,
            }
        return json_user

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % (self.nickname)

from . import login_manager

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    when = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_json(self):
        json_location = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'when': self.when.timestamp(),
                'who': url_for('api.get_user', id=self.user_id, _external=True)
            }
        return json_location

    @staticmethod
    def from_json(json_loc, uid):
        lat = json_loc.get('latitude')
        if lat is None or lat == '':
            raise ValidationError('Location is missing latitude')
        lng = json_loc.get('longitude')
        if lng is None or lng == '':
            raise ValidationError('Location is missing longitude')
        when = datetime.fromtimestamp(float(json_loc.get('when')), timezone.utc)
        if when is None or when == '':
            raise ValidationError('Location is missing a time stamp')
        return Location(latitude=float(lat), longitude=float(lng),
                        when=when, user_id=uid)

    @staticmethod
    def load_count(uid, count):
        results = Location.query.filter_by(user_id=uid).order_by(Location.when.desc())
        if count < 1:
            return results
        return results[:count]

    @staticmethod
    def load_date_range(uid, start, end, count=0):
        results = Location.query.filter(Location.user_id == uid, Location.when > start, Location.when < end).order_by(Location.when.desc())
        if count != 0:
            return results[:count]
        return results

    @staticmethod
    def delete_all_by_user(user):
        for loc in Location.query.filter_by(user_id=user.id):
            db.session.delete(loc)

    @staticmethod
    def delete_set(loc_ids, user):
        for id in loc_ids:
            loc = Location.query.filter_by(id=id).first()
            if loc.user_id == user.id:
                db.session.delete(loc)


class ReadPermission(db.Model):
    __tablename__ = 'read_permissions'
    id = db.Column(db.Integer, primary_key=True)
    grantor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    grantee_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_json(self):
        grantee = User.query.filter_by(id=grantee_id).first()
        json_permission = {
                   'id': grantee_id,
                    'nickname': grantee.nickname
                }
        return json_permission

    @staticmethod
    def from_json(json_perm):
        id = json_perm.get('id')
        if id is None or id == '':
            raise ValidationError('Permission does not have grantee id')
        return ReadPermission(grantee_id=id)

    @staticmethod
    def has_permission(target, reader):
        # A user always has permission to view their own data
        if target == reader:
            return True
        if ReadPermission.query.filter_by(grantor_id=target, grantee_id=reader).first() is not None:
            return True
        return False

