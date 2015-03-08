# -*- coding: utf-8 -*-

from .. import db

class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)

    admin = db.relationship('Admin', backref=db.backref('school', uselist=False))

    def __repr__(self):
        return '<School %d %s>' % (self.id, self.name)

class Building(db.Model):
    __tablename__ = 'building'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)

    school = db.relationship('School', backref=db.backref('buildings', lazy='dynamic'))
    admin = db.relationship('Admin', backref=db.backref('building', uselist=False))

    def __repr__(self):
        return '<Building %d %s>' % (self.id, self.name)

