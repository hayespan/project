# -*- coding: utf-8 -*-
from datetime import datetime
from .. import db

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    pic_id = db.Column(db.Integer, db.ForeignKey('file.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    cat2_id = db.Column(db.Integer, db.ForeignKey('cat2.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.Text(), nullable=False, default='')
    price = db.Column(db.Float, nullable=False)

    pic = db.relationship('File', backref=db.backref('product', uselist=False))
    cat2 = db.relationship('Cat2', backref=db.backref('products', lazy='dynamic'))

    def __repr__(self):
        return '<Product %d %s>' % (self.id, self.name)

class Product_building(db.Model):
    __tablename__ = 'product_building'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    timedelta = db.Column(db.Float, nullable=False)

    # redundance for order by performance
    sold_cnt_rd = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship('Product', backref=db.backref('product_buildings', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('product_buildings', lazy='dynamic'))

    def __repr__(self):
        return '<Product_building %d %d %d>' % (self.product_id, self.building_id, self.quantity)

class Snapshot(db.Model):
    __tablename__ = 'snapshot'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    pic_id = db.Column(db.Integer, db.ForeignKey('file.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    cat1_rd = db.Column(db.String(32), nullable=False)
    cat2_rd = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    released_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pic = db.relationship('File', backref=db.backref('snapshot', uselist=False))
    product = db.relationship('Product', backref=db.backref('snapshots', lazy='dynamic'))

    def __repr__(self):
        return '<Snapshot %d product_id:%d name:%s released_time:%s>' % (self.id, self.product_id or -1, self.name.encode('utf-8'), self.released_time)
