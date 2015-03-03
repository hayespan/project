# -*- coding: utf-8 -*-

from .. import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<User %d>' % (self.id)
