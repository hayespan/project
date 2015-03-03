# -*- coding: utf-8 -*-

from .. import db

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    ticketid = db.Column(db.String(21), nullable=False, default=lambda:datetime.now().strftime('%Y%m%d%H%M%S%f'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    room = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(15), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Enum('uncommited', 'uncompleted', 'completed', 'cancelled'), nullable=False, default='uncommited')
    eta = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(5), nullable=False, default=lambda: ''.join([str(random.choice(range(10))) for i in range(4)]))
    user = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('orders', lazy='dynamic'))

    def __repr__(self):
        return '<Order %d ticketid:%d user_id:%d building_id:%d' % (self.id, self.ticketid, self.user_id, self.building_id)

class Order_product(db.Model):
    __tablename__ = 'order_priduct'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order = db.relationship('Order', backref=db.backref('order_products', lazy='dynamic'))
    product = db.relationship('Order', backref=db.backref('order_products', lazy='dynamic'))
    def __repr__(self):
        return '<Order_product %d order_id:%d product_id:%d quantity:%d' % (self.id, self.order_id, self.product_id, self.quantity)
