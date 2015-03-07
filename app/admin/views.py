# -*- coding: utf-8 -*-

import os

from flask import request, session, g, render_template, redirect, url_for
from hashlib import md5

from . import adminbp 
from .models import Admin
# from .froms import *
from .utils import admin_login_required, get_order_money

from .. import db
from ..util.common import jsonError, jsonResponse
from ..util.errno import AdminErrno
from ..util.csrf import init_csrf_token, csrf_token_required
from ..location.models import Building, School
from ..order.models import Order, Order_snapshot
from ..product.models import Product, Product_building, Snapshot

# store the admin's information in the session
# session['admin_id'], session['admin_username'], session['_csrf_token'], session['admin_privilege']
# return the csrf token
# the privilege is 1, 2, 4 and if the privilege is 1, the admin got the highest priority
@adminbp.route('/login', methods=['POST', 'GET'])
def admin_login():
    session['admin_id'] = 1
    session['admin_username'] = 'raymond'
    session['_csrf_token'] = 'asdf'
    session['admin_privilege'] = 4
    return jsonResponse({'msg': 'login success.'})

@adminbp.route('/logout', methods=['POST',])
@admin_login_required
@csrf_token_required
def admin_logout():
    pass

@adminbp.route('/', methods=['GET',])
@admin_login_required
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
def refresh_admin():
    privilege = session.get('admin_privilege')
    if privilege == 4:
        return admin_level_3()
    elif privilege == 2:
        return admin_level_2()
    elif privilege == 1:
        return admin_level_1()
    else:
        return jsonError(AdminErrno.PRIVILEGE_ILLEGAL)

def admin_level_3():
    in_charge_order = []
    inventory = []
    try:
        admin = Admin.query.filter_by(id = session.get('admin_id')).first()
        admin_buildings = admin.buildings
        print '!' * 50
        print admin
        print admin_buildings
        orders = admin_buildings.orders
        print orders
    except:
        return jsonError(AdminErrno.NO_ORDER_IN_CHARGE)
    for o in orders:
        order = {'number': o.ticketid, 'details': [], 'receiver_info': {'name': o.receiver, 'location': o.room, 'phone': o.phone},
                 'status': o.status, 'released_time': o.released_time, 'timedelta': o.timedelta}
        snapshots = o.order_snapshots
        details = []
        for snapshot in snapshots:
            product = (Snapshot.query.filter_by(id = int(snapshot.snapshot_id)).first().name, snapshot.quantity)
            details.append(product)
        order['details'] = details
        in_charge_order.append(order)
    product = admin_buildings.product_buildings
    for product in products:
        inventory.append((Product.query.filter_by(id = int(product.product_id)).first().name, product.quantity))
    return jsonResponse({'orders' : in_charge_order, 'inventory' : inventory})

def admin_level_2():
    admin_school = Admin.query.filter_by(id = session.get('admin_id')).schools
    admin_buildings = admin_school.buildings
    # return all the building's name and id in this school to the front-end
    buildings = []
    for building in admin_buildings:
        buildings.append((building.name, building.id))
    # get the id of building which the front-end wants to query the order
    try:
        order_building = request.args.get('order_building')
        inventory_building = request.args.get('inventory_building')
    except:
        return jsonResponse({'buildings': buildings})
    orders_in_charge = []
    # if there is a building been selected
    if order_building:
        try:
            orders = Building.query.filter_by(id = int(order_building)).first().orders
        except Exception as e:
            return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
        for order in orders:
            if order.released_time.month == datetime.now().month:
                orders_in_charge.append({'released_time': order.released_time,
                                         'receiver_info': {'name': order.receiver, 'location': order.addr, 'phone': order.phone},
                                         'money': get_order_money(order),
                                         'status': order.status})
    # get the inventory information
    inventory_info = []
    if inventory_building:
        try:
            products = Building.query.filter_by(id = int(inventory_building)).first().product_buildings
        except Exception as e:
            return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)

        for product in products:
            inventory_info.append((Product.query.filter_by(id = int(product.product_id)).first().name, product.quantity))
    # get the total sales
    total_sales_building = request.args.get('total_sales_building')
    money = 0
    if total_sales_building == 'all':
        for building in admin_buildings:
            orders = building.orders
            for order in orders:
                money = money + get_order_money(order)
    else:
        try:
            orders = Building.query.filter_by(id = int(total_sales_building)).first().orders
        except Exception as e:
            return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
        else:
            for order in orders:
                money = money + get_order_money(order)
    return jsonResponse({'buildings': buildings, 'orders': orders_in_charge, 'inventory': inventory_info, 'total_sales': money})

def admin_level_1():
    schools = School.query.all()
    school_buildings = []
    for school in schools:
        s = {'name': school.name, 'school_id': school.id, 'buildings': []}
        buildings = schools.buildings
        for building in buildings:
            s['buildings'].append((building.name, building.id))
        schools_buildings.append(s)

    try:
        is_all_schools = bool(request.args.get('is_all'))
        (year, quarter, month) = request.args.get('time_range').split('/')
    except:
        return jsonError(AdminErrno.NOT_ENOUGH_ARGS)
    orders = []
    if is_all_schools:
        orders = Order.query.all()
    else:
        try:
            school = request.args.get('school')
            building = request.args.get('building')
        except:
            return jsonError(AdminErrno.NOT_ENOUGH_ARGS)
        if building == 'all':
            orders = School.query.filter_by(id = int(school)).first().buildings.orders
        else:
            orders = Building.query.filter_by(id = int(building)).first().orders
    money = 0
    for order in orders:
        try:
            if (order.released_time.year == int(year)) and is_in_same_quarter(order.released_time.month, int(quarter)) and is_in_same_month(order.released_time.month, month):
                money = money + get_order_money(order)
        except Exception as e:
            return jsonError(AdminErrno.TIME_ILLEGAL)

    return jsonResponse({'schools_buildings': schools_buildings, 'total_sales' : money})
        

@adminbp.route('/change_password', methods=['POST',])
@admin_login_required
@csrf_token_required
def admin_change_password():
    pass

@adminbp.route('/administrator', methods=['GET',])
@admin_login_required
@csrf_token_required
def manage_admin():
    pass

@adminbp.route('/administrator/add', methods=['POST',])
@csrf_token_required
def add_admin():
    admin = Admin(1, 'raymond', 'asdf', )

@adminbp.route('/administrator/edit', methods=['POST',])
@admin_login_required
@csrf_token_required
def edit_admin():
    pass

@adminbp.route('/administrator/delete', methods=['POST',])
@admin_login_required
@csrf_token_required
def admin_delete():
    pass
