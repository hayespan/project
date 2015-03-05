# -*- coding: utf-8 -*-

import os

from flask import request, session, g, render_template, redirect, url_for
from hashlib import md5

from . import adminbp 
from .models import Admin
from .froms import *
from .utils import admin_login_required

from .. import db
from ..util.common import jsonError, jsonResponse
from ..util.errno import AdminErrno
from ..util.csrf import init_csrf_token, csrf_token_required
from ..location.models import Building, School

# store the admin's information in the session
# session['admin_id'], session['admin_username'], session['_csrf_token'], session['admin_privilege']
# return the csrf token
# the privilege is 1, 2, 4 and if the privilege is 1, the admin got the highest priority
@adminbp.route('/login', methods=['POST', 'GET'])
def admin_login():
    pass

@adminbp.route('/logout', methods=['POST',])
@admin_login_required
@csrf_token_required
def admin_logout():
    pass

@adminbp.route('/', methods=['GET', 'POST'])
@admin_login_required
@csrf_token_required
def get_admin():
    privilege = session.get('admin_privilege')
    if privilege == 4:
        return render_template('index_3.html')
    elif privilege == 2:
        return render_template('index_2.html')
    elif privilege == 1:
        return render_template('index_1.html')
    else:
        return jsonError(AdminErrno.PRIVILEGE_ILLIGAL)

@adminbp.route('/refresh', methods=['GET',])
@admin_login_required
@csrf_token_required
def refresh_admin():
    privilege = session.get('admin_privilege')
    if privilege == 4:
        return admin_level_3
    elif privilege == 2:
        return admin_level_2
    elif privilege == 1:
        return admin_level_1
    else:
        return jsonError(AdminErrno.PRIVILEGE_ILLIGAL)

def admin_level_3():
    in_charge_order = []
    inventory = []
    in_charge_buildings = Building.query.filter_by(admin_id = int(session.get('admin_id')))
    if not in_charge_buildings:
        return jsonError(AdminErrno.NO_BUILDING_IN_CHARGE)
    for bd in in_charge_buildings:
        orders = Order.query.filter_by(building_id = bd.id)
        for order in orders:
            d = Order_product.query.filter_by(order_id = order.id)
            details = []
            for item in d:
                details.append((Product.query.filter_by(id = item.product_id).first().name, item.quantity))
            receiver = {'name' : order.receiver, 'location' : order.room, 'phone' : order.phone}
            in_charge_orders.append({'number' : order.ticketid, 'details' : d, 'receiver_info' : receiver,
                                     'status' : order.status, 'released_time' : order.released_time})
        products = Product_building.query.filter_by(building_id = bd.id)
        for item in products:
            inventory.append({'product' : Product.query.filter_by(id = item.product_id).first().name, 'quantity' : item.quantity})
    return jsonResponse({'orders' : in_charge_order, 'inventory' : inventory})

def admin_level_2():
    pass

def admin_level_1():
    pass

@adminbp.route('/change_password', methods=['POST',])
@admin_login_required
@csrf_token_required
def admin_change_password:
    pass

@adminbp.route('/administrator', method=['GET',])
@admin_login_required
@csrf_token_required
def manage_admin():
    pass

@adminbp.route('/administrator/add', method=['POST',])
@admin_login_required
@csrf_token_required
def add_admin():
    pass

@adminbp.route('/administrator/edit', method=['POST',])
@admin_login_required
@csrf_token_required
def edit_admin:
    pass

@adminbp.route('/administrator/delete', method=['POST',])
@admin_login_required
@csrf_token_required
def admin_delete():
    pass
