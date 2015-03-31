# -*- coding: utf-8 -*-
import random
from datetime import datetime

from .. import db

class Order(db.Model):
    __tablename__ = 'my_order'
    id = db.Column(db.Integer, primary_key=True)
    ticketid = db.Column(db.String(21), nullable=False, default=lambda:datetime.now().strftime('%Y%m%d%H%M%S%f'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    addr = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(15), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Enum('uncompleted', 'completed', 'cancelled'), nullable=False, default='uncompleted')
    released_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    timedelta = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(5), nullable=False, default=lambda: ''.join([str(random.choice(range(10))) for i in range(4)]))

    # redundancy information
    school_name_rd = db.Column(db.String(32), nullable=False)
    building_name_rd = db.Column(db.String(32), nullable=False)
    tot_price_rd = db.Column(db.Float, nullable=False) # for query performance
    sender_name_rd = db.Column(db.String(32), nullable=False, default='')
    sender_contact_info_rd = db.Column(db.String(100), nullable=False, default='')

    user = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('orders', lazy='dynamic'))

    def __repr__(self):
        return '<Order %d ticketid:%s user_id:%d building_id:%d>' % (self.id, self.ticketid, self.user_id, self.building_id)

class Order_snapshot(db.Model):
    __tablename__ = 'order_snapshot'
    order_id = db.Column(db.Integer, db.ForeignKey('my_order.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
    snapshot_id = db.Column(db.Integer, db.ForeignKey('snapshot.id', onupdate='CASCADE'), nullable=False, primary_key=True) # snapshot cannot be deleted
    quantity = db.Column(db.Integer, nullable=False, default=1)

    order = db.relationship('Order', backref=db.backref('order_snapshots', lazy='dynamic'))
    snapshot = db.relationship('Snapshot', backref=db.backref('order_snapshots', lazy='dynamic'))

    def __repr__(self):
        return '<Order_snapshot order_id:%d snapshot_id:%d quantity:%d>' % (self.order_id, self.snapshot_id, self.quantity)
