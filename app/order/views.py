# -*- coding: utf-8 -*-
import datetime

from flask import render_template ,g 

from . import orderbp
from .models import Order, Order_snapshot
from .forms import CreateOrderForm

from .. import db
from ..util.common import jsonResponse, jsonError, viaMobile
from ..util.errno import OrderErrno, CartErrno
from ..util.csrf import csrf_token_required
from ..user.utils import buyer_login_required

# ajax
@orderbp.route('/create', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def create_order():
    u = g.buyer
    form = CreateOrderForm()
    if form.validate_on_submit():
        product_ids = form.product_ids_list
        carts = [u.carts.filter_by(
                    product_id=i,
                    ).first() for i in product_ids
                    ]
        carts = u.carts.filter(Cart.product_id.in_(product_ids)).all()
        for i in carts:
            if not i.is_valid:
                return jsonError(CartErrno.CART_INVALID)
        pbs = [Product_building.query.filter_by(product_id=i.product_id, building_id=u.location_info['building_id']).first() for i in carts]
        if None in pbs:
            return jsonError(CartErrno.CART_INVALID)
        timedelta = max([i.timedelta for i in pbs])
        order = Order(
                user_id=u.id,
                building_id=u.location_info['building_id'],
                addr=form.addr.data,
                receiver=form.name.data,
                phone=form.phone.data,
                timedelta=timedelta,
                school_name_rd=u.location_info['school_name'],
                building_name_rd=u.location_info['building_name'],
                )
        db.session.add(order)
        # get right snapshot for association and calculate total price
        tot_price = 0
        for i in range(len(pbs)):
            pd = pbs[i].product
            sns = pd.snapshots.order_by('released_time desc').all() 
            for i in sns:
                if i.released_time < carts[i].last_viewed_time:
                    od_sn = Order_snapshot(
                            order=order,
                            snapshot=i,
                            quantity=carts[i].quantity,
                            )
                    db.session.add(od_sn)
                    tot_price += carts[i].quantity*i.price
                    break
        order.tot_price_rd = tot_price           
        # finally clear all items in cart
        u.carts.filter(Cart.product_id.in_(product_ids)).delete()
        db.session.commit()
        return jsonResponse(None)
    return jsonError(OrderErrno.INVALID_ARGUMENT)


@orderbp.route('/buyer', methods=['GET', ])
@buyer_login_required
def get_order_list():
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
    if viaMobile():
        return render_template('', user=u, orders=order_data)
    else:
        return render_template('', user=u, orders=order_data)

