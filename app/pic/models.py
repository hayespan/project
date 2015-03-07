# -*- coding: utf-8 -*-
from .. import db

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(40), nullable=False, index=True)

    def __repr__(self):
        return '<File %d %s>' % (self.id, self.filename)

class Promotion(db.Model):
    __tablename__ = 'promotion'
    id = db.Column(db.Integer, primary_key=True)
    pic_id =  db.Column(db.Integer, db.ForeignKey('file.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    pic = db.relationship('File', backref=db.backref('promotion', uselist=False))

    def __repr__(self):
        return '<Promotion %d pic_id:%d' % (self.id, self.pic_id)

