# -*- coding: utf-8 -*-

from .. import db

class Cart(db.Model):
    __tablename__ = 'cart'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_valid = db.Column(db.Boolean, nullable=False, default=True)
    user = db.relationship('User', backref=db.backref('carts', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('carts', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('carts', lazy='dynamic'))

    def __repr__(self):
        return '<Cart - user_id:%d building_id:%d product_id:%d quantity:%d>' % (self.user_id, self.building_id, self.product_id, self.quantity)
