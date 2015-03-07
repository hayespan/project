# -*- coding: utf-8 -*-

from datetime import datetime
from .. import db

class Cart(db.Model):
    __tablename__ = 'cart'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)

    # update only when user open cart
    last_viewed_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_valid = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship('User', backref=db.backref('carts', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('carts', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('carts', lazy='dynamic'))

    def __repr__(self):
        return '<Cart - user_id:%d building_id:%d product_id:%d quantity:%d>' % (self.user_id, self.building_id, self.product_id, self.quantity)
