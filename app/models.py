from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt
from time import time
from hashlib import md5


@login.user_loader
def load_user(id):
    return User.query.get(int(id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tasks = db.relationship(
        'Task', backref='author', lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return f'User: {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(64), default='Active', nullable=False)
    due_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    task_comments = db.relationship(
        'TaskComment', backref='task', lazy='dynamic', passive_deletes=True)


class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    body = db.Column(db.String(300), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='CASCADE'))
