# -*- coding: utf-8 -*-
import datetime
import time

from flask import session, g, render_template

from .. import db
from ..user.forms import CreateUserForm
from ..category.utils import _get_catx
from ..order.models import Order
from ..user.models import User
from ..util.csrf import init_csrf_token, csrf_token_required
from ..user.utils import buyer_login_required
from ..location.models import School, Building
from . import mobilebp

@mobilebp.route('/', methods=['GET', ])
def index():
    uid = session.get('buyerid')
    user = User.query.filter_by(id=uid).first() if uid else None
    if user:
        user.name = u'匿名用户'
    promotions = [i.pic.filename for i in Promotion.query.all()]
    return render_template('m/index.html', user=user, catx=_get_catx(), promotions=promotions)

@mobilebp.route('/locations', methods=['GET', ])
def get_locations():
    schools = School.query.all()
    locations = [[i, i.buildings.all()] for i in schools]
    return render_template('m/choose_location.html', locations=locations)

@mobilebp.route('/cart', methods=['GET', ])
@buyer_login_required(False, 'mbend.get_locations')
def cart_page():
    return render_template('m/cart.html')

@mobilebp.route('/order', methods=['GET', ])
@buyer_login_required(False, 'mbend.get_locations')
def order_page():
    u = g.buyer
    orders = u.orders.order_by(db.case([(Order.status=='uncompleted', 1),], else_=0).desc()).all()
    order_data = []
    for i in orders:
        data = dict()
        data['id'] = i.id
        data['ticketid'] = i.ticketid
        data['sender_name'] = i.sender_name_rd
        data['sender_contact_info'] = i.sender_contact_info_rd
        data['price'] = i.tot_price_rd
        data['released_time'] = i.released_time
        td =  datetime.timedelta(hours=i.timedelta)
        data['timedelta'] = td
        data['delivery_timestamp'] = int(time.mktime(time.strptime(str(i.released_time+td), '%Y-%m-%d %H:%M:%S.%f')))
        data['timeout'] = i.released_time+td<=datetime.datetime.now()
        data['password'] = i.password
        data['status'] = i.status
        items = []
        for j in i.order_snapshots.all():
            sn = j.snapshot
            item_meta = dict()
            item_meta['id'] = sn.id # snapshot id
            item_meta['filename'] = sn.pic.filename
            item_meta['name'] = sn.name
            item_meta['description'] = sn.description
            item_meta['price'] = sn.price
            item_meta['quantity'] = j.quantity
            items.append(item_meta)
        data['items'] = items
        order_data.append(data) 
    return render_template('m/order.html', user=u, orders=order_data)
