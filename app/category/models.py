# -*- coding: utf-8 -*-

from .. import db

class Cat1(db.Model):
    __tablename__ = 'cat1'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    def __repr__(self):
        return '<Cat1 %d %s>' % (self.id, self.name)

class Cat2(db.Model):
    __tablename__ = 'cat2'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    cat1_id = db.Column(db.Integer, db.ForeignKey('cat1.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False) 

    cat1 = db.relationship('Cat1', backref=db.backref('cat2s', lazy='dynamic'))

    def __repr__(self):
        return '<Cat2 %d %s>' % (self.id, self.name)

