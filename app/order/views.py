# -*- coding: utf-8 -*-
import datetime
import time

from flask import render_template, g, session

from . import orderbp
from .models import Order, Order_snapshot
from .forms import CreateOrderForm

from .. import db
from ..util.common import jsonResponse, jsonError, viaMobile
from ..util.errno import OrderErrno, CartErrno
from ..util.csrf import csrf_token_required
from ..user.utils import buyer_login_required
from ..cart.models import Cart
from ..product.models import Product_building, Product, Snapshot
from ..location.models import Building, School
from ..util.common import PC_MB_distribute

# ajax
@orderbp.route('/create', methods=['POST', ])
@buyer_login_required(True)
@csrf_token_required
def create_order():
    u = g.buyer
    form = CreateOrderForm()
    if form.validate_on_submit():
        product_ids = form.product_ids_list
        carts = u.carts.filter(Cart.product_id.in_(product_ids)).all()
        for i in carts: # check whether post invalid id
            if not i.is_valid:
                return jsonError(CartErrno.CART_INVALID)
        pbs = [Product_building.query.filter_by(product_id=i.product_id, building_id=u.location_info['building_id']).first() for i in carts]
        if None in pbs: # check whether all product are accessible
            return jsonError(CartErrno.CART_INVALID)
        for i in range(len(pbs)): # check whether some products have been updated
            pd = pbs[i].product
            if pd.snapshots.filter(Snapshot.released_time>carts[i].last_viewed_time).count() or\
                    pbs[i].quantity < carts[i].quantity:
                return jsonError(OrderErrno.PRODUCT_REFRESH)
        timedelta = max([i.timedelta for i in pbs]) # get max delivery time
        bd = Building.query.get(u.location_info['building_id'])
        order = Order(
                user_id=u.id,
                building_id=u.location_info['building_id'],
                addr=form.addr.data,
                receiver=form.name.data,
                phone=form.phone.data,
                timedelta=timedelta,
                school_name_rd=bd.school.name,
                building_name_rd=bd.name,
                sender_name_rd=bd.admin.name,
                sender_contact_info_rd=bd.admin.contact_info,
                tot_price_rd=0,
                )
        session['buyer_contact_info'] = [form.name.data, form.phone.data, form.addr.data]
        # get most recent snapshot for association and calculate total price
        tot_price = 0
        od_sn_list = []
        for i in range(len(pbs)):
            pd = pbs[i].product
            sn = pd.snapshots.order_by(Snapshot.released_time.desc()).first()
            od_sn = Order_snapshot(
                    order=order,
                    snapshot=sn,
                    quantity=carts[i].quantity,
                    )
            od_sn_list.append(od_sn)
            tot_price += carts[i].quantity*sn.price
        order.tot_price_rd = tot_price
        db.session.add(order)
        for i in od_sn_list:
            db.session.add(i)
        # finally clear all items in cart
        u.carts.filter(Cart.product_id.in_(product_ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonResponse(None)
    return jsonError(OrderErrno.INVALID_ARGUMENT)

@orderbp.route('/', methods=['GET', ])
@PC_MB_distribute('/m/order')
@buyer_login_required(False, 'main.index')
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
        data['released_time'] = int(time.mktime(time.strptime(str(i.released_time), '%Y-%m-%d %H:%M:%S')))
        data['released_time_str'] = i.released_time.strftime('%Y-%m-%d')
        td =  datetime.timedelta(hours=i.timedelta)
        data['timedelta'] = i.timedelta*3600
        data['delivery_timestamp'] = int(time.mktime(time.strptime(str(i.released_time+td), '%Y-%m-%d %H:%M:%S')))
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
    return render_template('pc/orders_list_page.html', user=u, orders=order_data)

@orderbp.route('/list', methods=['POST', ])
@buyer_login_required(True)
@csrf_token_required
def get_order_list():
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
        data['released_time'] = int(time.mktime(time.strptime(str(i.released_time), '%Y-%m-%d %H:%M:%S')))
        td =  datetime.timedelta(hours=i.timedelta)
        data['timedelta'] = i.timedelta*3600
        data['delivery_timestamp'] = int(time.mktime(time.strptime(str(i.released_time+td), '%Y-%m-%d %H:%M:%S')))
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
    return jsonResponse(order_data)
