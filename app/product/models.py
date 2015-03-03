# -*- coding: utf-8 -*-

from .. import db

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    pic_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)
    cat2_id = db.Column(db.Integer, db.ForeignKey('cat2.id'), nullable=True)
    description = db.Column(db.Text(), nullable=False, default='')
    price = db.Column(db.Float, nullable=False)

    pic = db.relationship('File', backref=db.backref('product', uselist=False))
    cat2 = db.relationship('Cat2', backref=db.backref('products', lazy='dynamic'))

    def __repr__(self):
        return '<Product %d %s>' % (self.id, self.name)

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(40), nullable=False, index=True)

    def __repr__(self):
        return '<File %d %s>' % (self.id, self.filename)

class Product_building(db.Model):
    __tablename__ = 'product_building'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    eta = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref=db.backref('product_buildings', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('product_buildings', lazy='dynamic'))

    def __repr__(self):
        return '<Product_building %d %d %d>' % (self.product_id, self.building_id, self.quantity)

class Promotion(db.Model):
    __tablename__ = 'promotion'
    id = db.Column(db.Integer, primary_key=True)
    pic_id =  db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)

    pic = db.relationship('File', backref=db.backref('promotion', uselist=False))

    def __repr__(self):
        return '<Promotion %d pic_id:%d' % (self.id, self.pic_id)

