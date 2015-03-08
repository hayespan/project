# -*- coding: utf-8 -*-

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    privilege = db.Column(db.Integer, nullable=False, default=1)
    name = db.Column(db.String(32), nullable=False, default='')
    contact_info = db.Column(db.String(100), nullable=False, default='')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Admin %d %s>' % (self.id, self.username)

