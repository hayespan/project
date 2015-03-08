# -*- coding: utf-8 -*-

import os
from hashlib import md5
import datetime

from flask import request, session, g, render_template, redirect, url_for, abort

from . import adminbp 
from .models import Admin
from .forms import LoginForm
from .utils import admin_login_required, is_in_same_quarter, is_in_same_month, admin_x_required

from .. import db
from ..util.common import jsonError, jsonResponse, datetime_2_unixstamp, timedelta_2_second, viaMobile
from ..util.errno import AdminErrno
from ..util.csrf import init_csrf_token, csrf_token_required
from ..location.models import Building, School
from ..order.models import Order, Order_snapshot
from ..product.models import Product, Product_building, Snapshot

# store the admin's information in the session
# session['admin_id'], session['_csrf_token']
# return the csrf token
# the privilege is 1, 2, 4 and if the privilege is 1, the admin got the highest priority
@adminbp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        admin_id = session.get('admin_id')
        csrf_token = session.get('_csrf_token')
        if (admin_id and csrf_token and Admin.query.filter_by(id=admin_id).count()):
            return redirect(url_for('.index'))
        return render_template('admin-login.html')
    elif request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            admin = Admin.query.filter_by(username=form.username.data).first()
            if admin is None:
                return jsonError(AdminErrno.ADMIN_DOES_NOT_EXIST)
            if admin.verify_password(form.password.data):
                if viaMobile() and admin.privilege in [1, 2, ]:
                    return jsonError(AdminErrno.PERMISSION_DENIED)
                session['admin_id'] = admin.id
                init_csrf_token()
                return jsonResponse({'_csrf_token': session['_csrf_token']})
            return jsonError(AdminErrno.AUTHENTICATION_FAILED)
        return jsonError(AdminErrno.INVALID_ARGUMENT)
    else:
        abort(404)

@adminbp.route('/logout', methods=['POST',])
@admin_login_required(True)
@csrf_token_required
def logout():
    session.pop('admin_id', None)
    session.pop('_csrf_token', None)
    return jsonResponse(None)

@adminbp.route('/index', methods=['GET',])
@admin_login_required(False, 'admin.login')
def index():
    ad = g.admin
    if ad.privilege == 4:
        if not viaMobile():
            return render_template('index_3.html')
        else:
            return render_template('index_3_m.html')
    elif ad.privilege == 2:
        return render_template('index_2.html')
    elif ad.privilege == 1:
        return render_template('index_1.html')
    else:
        abort(404)

@adminbp.route('/level3/query', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(4)
@csrf_token_required
def admin_3rd_api():
    return _admin_level_3()

@adminbp.route('/level2/query', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(2)
@csrf_token_required
def admin_2nd_api():
    return _admin_level_2()

def _admin_level_3():
    '''APIs for 3rd admin.
    '''
    admin = g.admin
    admin_building = admin.building
    if not admin_building:
        return jsonError(AdminErrno.NO_BUILDING_IN_CHARGE)
    time_ = _get_time_()
    
    # get order list
    in_charge_order = []
    get_order_list = request.args.get('get_order_list', 0, type=int)
    if get_order_list:
        orders = admin_building.orders.\
                filter(Order.released_time>=time_).\
                order_by(db.case([(Order.status=='uncompleted', 1), ],
                    else_=0).desc()).all()
        for o in orders:
            order = {
                    'number': o.ticketid,
                    'details': [],
                    'receiver_info': {
                        'name': o.receiver,
                        'location': o.addr,
                        'phone': o.phone
                        },
                    'status': o.status,
                    'released_time': datetime_2_unixstamp(o.released_time),
                    'timedelta': timedelta_2_second(o.timedelta),
                    'timeout': o.released_time+datetime.timedelta(hours=o.timedelta)<datetime.datetime.now(),
                    }
            snapshots = o.order_snapshots
            details = []
            for snapshot in snapshots:
                sn = Snapshot.query.filter_by(id = int(snapshot.snapshot_id)).first()
                product = {
                        'name': sn.name,
                        'price': sn.price,
                        'quantity': snapshot.quantity,
                        }
                details.append(product)
            order['details'] = details
            in_charge_order.append(order)

    # get inventory
    inventory = []
    get_inventory_list = request.args.get('get_inventory_list', 0, type=int)
    if get_inventory_list:
        products = admin_building.product_buildings.all()
        for product in products:
            pd = Product.query.filter_by(id = int(product.product_id)).first()
            data = {
                    'name': pd.name,
                    'description': pd.description,
                    'quantity': product.quantity,
                    }
            inventory.append(data)

    return jsonResponse({
        'orders': in_charge_order,
        'inventory': inventory,
        })

def _admin_level_2():
    '''APIs for 2nd admin.
    '''
    admin = g.admin
    admin_school = admin.school
    admin_buildings = admin_school.buildings.all()
    time_ = _get_time_()
    if not admin_school:
        return jsonError(AdminErrno.NO_SCHOOL_IN_CHARGE)

    # get the id of building which the front-end wants to query the order
    get_building_list = request.args.get('get_building_list', None, type=int)
    building_data = []
    if get_building_list is not None:
        # return all the building's name and id in this school to the front-end
        for building in admin_buildings:
            building_data.append({
                'id': building.id,
                'name': building.name, 
                })

    # get orders
    order_building = request.args.get('get_order_list', None, type=int)
    orders_in_charge = []
    if order_building is not None:
        # if there is a building been selected
        sc = admin_school
        if order_building >= 0:
            bd = sc.buildings.filter_by(id=order_building.id).first()
            # building not in your charge
            if not bd:
                return jsonError(AdminErrno.PERMISSION_DENIED)
            order_base_q = bd.orders
        # if < 0, not filter
        else:
            orders_base_q = Order.query.filter(Order.building_id.in_([i.id for i in admin_buildings]))
        # order
        orders = order_base_q.filter_by(Order.released_time>=time_).\
                    order_by(Order.released_time.desc()).all()
        for order in orders:
            orders_in_charge.append({
                'released_time': datetime_2_unixstamp(order.released_time),
                'receiver_info': {
                    'name': order.receiver,
                    'location': order.addr,
                    'phone': order.phone
                    },
                 'money': order.tot_price_rd,
                 'status': order.status
                 })

    # get inventory
    inventory_building = request.args.get('get_inventory_list',None, type=int)
    inventory_info = []
    if inventory_building is not None:
        # get the inventory information
        sc = admin_school
        if inventory_building >= 0:
            bd = sc.buildings.filter_by(id=order_building.id).first()
            # building not in your charge
            if not bd:
                return jsonError(AdminErrno.PERMISSION_DENIED)
            pd_bd_base_q = bd.product_buildings
        else:
            pd_bd_base_q = Product_building.query.filter(Product_building.building_id.in_([i.id for i in admin_buildings]))
        pd_bds = pd_bd_base_q.order_by(Product_building.quantity).all()
        for pd_bd in pd_bds:
            pd = pd_bd.product
            inventory_info.append({
                'id': pd.id,
                'name': pd.name,
                'description': pd.name, 
                'price': pd.price,
                'quantity': pd_bd.quantity
                })

    # get the total sales
    total_sales_building = request.args.get('get_total_sales', None, type=int)
    money = 0
    amount = 0
    now = datetime.datetime.now()
    if total_sales_building is not None:
        # all building
        if total_sales_building == -1:
            for building in admin_buildings:
                orders = building.orders.filter(
                            Order.status=='completed',
                            db.func.year(Order.released_time)==now.year,
                            db.func.month(Order.released_time)==now.month).all()
                amount = amount + len(orders)
                for order in orders:
                    money = money + order.tot_price_rd
        else:
            sc = admin_school
            bd = sc.buildings.filter(Building.id==total_sales_building).first()
            # building not in your charge
            if not bd:
                return jsonError(AdminErrno.PERMISSION_DENIED)
            orders = bd.orders.filter(
                    Order.status=='completed',
                    db.func.year(Order.released_time)==now.year,
                    db.func.month(Order.released_time)==now.month).all()
            amount = len(orders)
            for order in orders:
                money = money + order.tot_price_rd

    return jsonResponse({
        'buildings': building_data,
        'orders': orders_in_charge,
        'inventory': inventory_info,
        'total_sales': {
            'amount': amount,
            'money': money
            },
        })

# TODO 一级管理页面还没整理
def admin_level_1():
    '''APIs for 1st admin.
    '''
    schools = School.query.all()
    school_buildings = []
    for school in schools:
        s = {'name': school.name, 'school_id': school.id, 'buildings': []}
        buildings = school.buildings.all()
        for building in buildings:
            s['buildings'].append((building.name, building.id))
        school_buildings.append(s)
    try:
        is_all_schools = bool(request.args.get('is_all', 'True'))
        (year, quarter, month) = request.args.get('time_range', str(datetime.now().year)+'/all/all').split('/')
    except:
        return jsonError(AdminErrno.NOT_ENOUGH_ARGS)
    orders = []
    if is_all_schools:
        orders = Order.query.all()
    else:
        school = request.args.get('school')
        building = request.args.get('building')
        if not (school or building):
            return jsonError(AdminErrno.NOT_ENOUGH_ARGS)
        if building == 'all':
            orders = School.query.filter_by(id = int(school)).first().buildings.orders
        else:
            orders = Building.query.filter_by(id = int(building)).first().orders
    money = 0
    if month != 'all' and quarter != 'all':
        if not (is_in_same_quarter(int(month), int(quarter))):
            return jsonError(AdminErrno.TIME_ILLEGAL)
    for order in orders:
        if (order.released_time.year == int(year)) and ((quarter == 'all') or is_in_same_quarter(order.released_time.month, int(quarter))) and (month == 'all' or is_in_same_month(order.released_time.month, month)):
            money = money + get_order_money(order)

    return jsonResponse({'schools_buildings': school_buildings, 'total_sales' : money})
        

@adminbp.route('/change_password', methods=['POST',])
@admin_login_required(True)
@csrf_token_required
def admin_change_password():
    pass

@adminbp.route('/administrator', methods=['GET',])
@admin_login_required(True)
@csrf_token_required
def manage_admin():
    pass

@adminbp.route('/administrator/add', methods=['POST',])
@csrf_token_required
def add_admin():
    pass

@adminbp.route('/administrator/edit', methods=['POST',])
@admin_login_required(True)
@csrf_token_required
def edit_admin():
    pass

@adminbp.route('/administrator/delete', methods=['POST',])
@admin_login_required(True)
@csrf_token_required
def admin_delete():
    pass

def _get_time_():
    return datetime.datetime.now()-datetime.timedelta(days=30)

