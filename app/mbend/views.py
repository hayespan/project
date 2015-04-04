# -*- coding: utf-8 -*-
import datetime
import time

from flask import session, g, render_template, request, abort

from .. import db
from ..user.forms import CreateUserForm
from ..category.utils import _get_catx
from ..order.models import Order
from ..user.models import User
from ..util.csrf import init_csrf_token, csrf_token_required
from ..user.utils import buyer_login_required
from ..location.models import School, Building
from ..pic.models import Promotion
from ..product.views import _get_product_list
from ..category.models import Cat1, Cat2
from . import mobilebp

@mobilebp.route('/', methods=['GET', ])
def index():
    uid = session.get('buyerid')
    user = User.query.filter_by(id=uid).first() if uid else None
    if user:
        buyer_contact_info = session.get('buyer_contact_info')
        if buyer_contact_info:
            user.name = buyer_contact_info[0]
        else:
            user.name = u'匿名用户'
        buyer_location_info = session.get('buyer_location_info')
        user.location_info = {
                'school_id': buyer_location_info[0][0],
                'school_name': buyer_location_info[0][1],
                'building_id': buyer_location_info[1][0],
                'building_name': buyer_location_info[1][1],
                }
    promotions = [i.pic.filename for i in Promotion.query.all()]
    return render_template('mb/index.html', user=user, catx=_get_catx(), promotions=promotions)

@mobilebp.route('/locations', methods=['GET', ])
def location_page():
    schools = School.query.all()
    locations = [[i, i.buildings.all()] for i in schools]
    return render_template('mb/location_page.html', locations=locations)

@mobilebp.route('/cart', methods=['GET', ])
@buyer_login_required(False, 'mbend.location_page')
def cart_page():
    return render_template('mb/cart_page.html')

@mobilebp.route('/product/list', methods=['GET', ])
@buyer_login_required(False, 'mbend.location_page')
def product_page():
    u = g.buyer
    bd = u.building
    cat2_id = request.args.get('cat2', type=int)
    if cat2_id is None:
        abort(404)
    try:
        cat2 = Cat2.query.get(cat2_id)
        if cat2 is None:
            abort(404)
        cat1 = cat2.cat1
        pds, current_cat1 = _get_product_list(bd, cat2_id=cat2_id)
    except:
        abort(404)
    return render_template('mb/product_page.html', user=u, current_cat1=cat1, current_cat2=cat2, products=pds)

@mobilebp.route('/order', methods=['GET', ])
@buyer_login_required(False, 'mbend.location_page')
def order_page():
    u = g.buyer
    orders = u.orders.order_by(db.case([(Order.status=='uncompleted', Order.id),], else_=-1).desc()).all()
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
        data['timedelta'] = i.released_time+td-datetime.datetime.now()
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
    return render_template('mb/order_page.html', user=u, orders=order_data)

