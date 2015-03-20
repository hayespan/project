# -*- coding: utf-8 -*-
import os
import datetime
from hashlib import md5

from flask import request, session, g, render_template, redirect, url_for, abort

from . import adminbp 
from .models import Admin
from .forms import *
from .utils import admin_login_required, is_in_same_quarter, is_in_same_month, admin_x_required, parse_quarter_2_month

from .. import db
from ..util.common import jsonError, jsonResponse, datetime_2_unixstamp, timedelta_2_second, viaMobile
from ..util.errno import AdminErrno
from ..util.csrf import init_csrf_token, csrf_token_required
from ..util.exportxls import export_xls, export_product_xls
from ..location.models import Building, School
from ..order.models import Order, Order_snapshot
from ..product.models import Product, Product_building, Snapshot
from ..category.models import Cat1, Cat2
from ..pic.utils import savepic, changepic, removepic, copypic

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

## admin 3rd's api
@adminbp.route('/level3/query', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(4)
@csrf_token_required
def admin_3rd_api():
    return _admin_level_3()

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

@adminbp.route('/level3/handle_order', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(4)
@csrf_token_required
def admin_3rd_handle_order():
    '''handle order, complete or cancel
    '''
    form = HandleOrderForm()
    if form.validate_on_submit():
        ticketid = form.ticketid.data
        password = form.password.data
        handle = form.handle.data
        order = Order.query.filter(Order.ticketid==ticketid).first()
        if not order:
            return jsonError(AdminErrno.ORDER_DOES_NOT_EXIST)
        if order.status != 'uncompleted':
            return jsonError(AdminErrno.ORDER_HANDLED)
        if order.password == password:
            order.status = 'completed' if handle else 'cancelled'
            db.session.add(order)
        # if complete order, fresh inventory & total sales
        if handle:
            od_sns = order.order_snapshots.all()
            for od_sn in od_sns:
                pd = od_sn.snapshot.product
                if pd:
                    pd_bd = pd.product_buildings.filter(Product_building.building_id==order.building_id).first()
                    if pd_bd:
                        pd_bd.quantity -= od_sn.quantity
                        pd_bd.sold_cnt_rd += od_sn.quantity
                        db.session.add(pd_bd)
        # if cancel order, do nothing
        else:
            pass
        db.session.commit()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

## admin 2nd's api
@adminbp.route('/level2/query', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(2)
@csrf_token_required
def admin_2nd_api():
    return _admin_level_2()

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

@adminbp.route('/level2/modify_quantity', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(2)
@csrf_token_required
def admin_2nd_modify_quantity():
    '''2nd admin modify product_building.quantity, sub/add
    '''
    ad = g.admin
    sc = ad.school
    if not sc:
        return jsonError(AdminErrno.NO_SCHOOL_IN_CHARGE)
    form = ModifyQuantityForm()
    if form.validate_on_submit():
        product_id = form.producct_id.data
        quantity = form.quantity.data
        building_id = form.building_id.data
        if not sc.buildings.filter(Building.id==building_id).count():
            return jsonError(AdminErrno.PERMISSION_DENIED)
        pd_bd = Product_building.query.filter(Product_building.building_id==building_id, Product_building.product_id==product_id).first()
        if not pd_bd:
            return jsonError(AdminErrno.PRODUCT_DISASSO_WITH_BUILDING)
        if quantity >= 0:
            pd_bd.quantity += quantity
        else:
            pd_bd.quantity += quantity
            if pd_bd.quantity < 0:
                pd_bd.quantity = 0
        db.session.add(pd_bd)
        db.session.commit()
        return jsonResponse(pd_bd.quantity)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

## admin 1st's api
@adminbp.route('/level1/total_sales', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_total_sales():
    '''APIs for 1st admin.
    school_id:
    building_id:
    year:
    quarter:
    month:
    export:
    '''
    school_id = request.args.get('school_id', None, type=int)
    if school_id is None:
        q1 = Order.query
    else:
        sc = School.query.filter_by(id=school_id).first()
        if not sc:
            return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
        q1 = db.session.query(Order).\
                join(Building, Order.building_id==Building.id).\
                join(School, Building.school_id==School.id).\
                filter(School.id==sc.id)

    building_id = request.args.get('building_id', None ,type=int)
    if building_id is None:
        q2 = q1
    else:
        bd = Building.query.filter_by(id=building_id).first()
        if not bd:
            return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
        q2 = q1.filter(Order.building_id==bd.id)

    year = request.args.get('year', None, type=int)
    if year is None:
        q3 = q2
    else:
        q3 = q2.filter(db.func.year(Order.released_time)==year)

    quarter = request.args.get('quarter', None, type=int)
    if quarter is None:
        q4 = q3
    else:
        q4 = q3.filter(db.func.month(Order.released_time).in_(parse_quarter_2_month(quarter)))

    month = request.args.get('month', None, type=int)
    if month is None:
        q5 = q4
    else:
        q5 = q4.filter(db.func.month(Order.released_time)==(month-1)%12+1)
    # export order excel
    export = request.args.get('export', 0, type=int)
    if export == 1:
        orders = q5.order_by(Order.released_time).all()
        fn = export_xls(orders)
        return jsonResponse(url_for('static', filename='tmp/'+fn))
    # get total sales
    orders = q5.filter(status=='completed').all()
    total_sales = 0
    for i in orders:
        total_sales += i.tot_price_rd
    return jsonResponse(total_sales)

# School ---- get, insert, modify, delete
@adminbp.route('/level1/school/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_school_list():
    scs = []
    for i in School.query.all():
        scs.append({
            'id':i.id,
            'name': i.name,
            })
    return jsonResponse(scs)

@adminbp.route('/level1/school/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_school():
    form = CreateSchoolForm()
    if form.validate_on_submit():
        name = form.name.data
        if School.query.filter_by(name=name).count():
            return jsonError(AdminErrno.SCHOOL_EXISTS)
        sc = School(name=name)
        db.session.add(sc)
        db.session.commit()
        return jsonResponse({
            'id': sc.id,
            'name': sc.name,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/school/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_school():
    form = ModifySchoolForm()
    if form.validate_on_submit():
        school_id = form.school_id.data
        sc = School.query.get(school_id)
        if not sc:
            return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
        name = form.name.data
        if sc.name == name:
            pass
        else:
            if School.query.filter_by(name=name).count():
                return jsonError(AdminErrno.SCHOOL_EXISTS)
            sc.name = name
            db.session.add(sc)
            db.session.commit()
        return jsonResponse({
            'id': sc.id,
            'name': sc.name,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/school/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_school():
    form = DeleteSchoolForm()
    if form.validate_on_submit():
        School.query.filter_by(id=form.school_id.data).delete()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

# Building ---- get, insert, update, delete
@adminbp.route('/level1/building/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_building_list():
    form = GetBuildingListForm()
    if form.validate_on_submit():
        sc_id = form.school_id.data
        sc = School.query.get(sc_id)
        if not sc:
            return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
        bds = []
        for i in sc.buildings.all():
            bds.append({
                'id': i.id,
                'name': i.name,
                })
        return jsonResponse(bds)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/building/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_building():
    form = CreateBuildingForm()
    if form.validate_on_submit():
        sc_id = form.school_id.data
        name = form.name.data
        sc = School.query.get(sc_id)
        if not sc:
            return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
        bd = Building(name=name)
        bd.school = sc
        db.session.add(bd)
        db.session.commit()
        return jsonResponse({
            'id': bd.id,
            'name': bd.name,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/building/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_building():
    form = ModifyBuildingForm()
    if form.validate_on_submit():
        bd = Building.query.get(form.building_id.data)
        if not bd:
            return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
        name = form.name.data
        if bd.name == name:
            pass
        else:
            if Building.query.get(name=name).count():
                return jsonError(AdminErrno.BUILDING_EXISTS)
            bd.name = name
            db.session.add(bd)
            db.session.commit()
        return jsonResponse({
            'id': bd.id,
            'name': bd.name,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/building/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_building():
    form = DeleteBuildingForm()
    if form.validate_on_submit():
        bd_id = form.building_id.data
        Building.query.filter_by(id=bd_id).delete()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

# 2nd_admin ---- get, insert, modify, delete
@adminbp.route('/level1/admin_2nd/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_admin_2nd_list():
    ads = []
    for i in Admin.query.all():
        sc = i.school
        if sc:
            sc_info = {
                    'id': sc.id,
                    'name': sc.name,
                    }
        else:
            sc_info = None
        ads.append({
            'id': i.id,
            'username': i.username,
            'name': i.name,
            'contact_info': i.contact_info,
            'school_info': sc_info,
            })
    return jsonResponse(ads)

@adminbp.route('/level1/admin_2nd/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_admin_2nd():
    form = CreateAdmin2ndForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        name = form.name.data
        contact_info = form.contact_info.data
        school_id = form.school_id.data
        if Admin.query.filter_by(username=username).count():
            return jsonError(AdminErrno.ADMIN_EXISTS)
        sc = None
        if school_id is not None:
            sc = School.query.get(school_id)
            if not sc:
                return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
            if sc.admin:
                return jsonError(AdminErrno.SCHOOL_BEING_OCCUPIED)
        ad = Admin(
                username=username,
                name=name,
                contact_info=contact_info,
                )
        ad.password = password
        ad.school = sc
        db.session.add(ad)
        db.session.commit()
        return jsonResponse({
            'id': ad.id,
            'username': ad.username,
            'school_info': {
                'id': ad.school.id,
                'name': ad.school.name,
                } if ad.school else None
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/admin_2nd/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_admin_2nd():
    form = ModifyAdmin2ndForm()
    if form.validate_on_submit():
        admin_id = form.admin_id.data
        username = form.username.data
        password = form.password.data
        name = form.name.data
        contact_info = form.contact_info.data
        school_id = form.school_id.data
        ad = Admin.query.get(admin_id)
        if not ad:
            return jsonError(AdminErrno.ADMIN_DOES_NOT_EXIST)
        if ad.username != username:
            if Admin.query.filter_by(username=username).count():
                return jsonError(AdminErrno.USERNAME_EXISTS)
            ad.username = username
        if password:
            ad.password = password
        ad.name = name
        ad.contact_info = contact_info
        if school_id is None:
            ad.school = None
        else:
            sc = School.query.get(school_id)
            if not sc:
                return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
            if ad.school:
                if ad.school.id == sc.id:
                    pass
                else:
                    if sc.admin:
                        return jsonError(AdminErrno.SCHOOL_BEING_OCCUPIED)
                    else:
                        ad.school = sc
            else:
                if sc.admin:
                    return jsonError(AdminErrno.SCHOOL_BEING_OCCUPIED)
                else:
                    ad.school = sc
        db.session.add(ad)
        db.session.commit()
        return jsonResponse({
            'id': ad.id,
            'username': ad.username,
            'school_info': {
                'id': ad.school.id,
                'name': ad.school.name,
                } if ad.school else None
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/admin_2nd/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_admin_2nd():
    form = DeleteAdmin2ndForm()
    if form.validate_on_submit():
        ad_id = form.admin_id.data
        Admin.query.filter_by(id=ad_id).delete()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

# XXX
@adminbp.route('/level1/admin_2nd/unbind_school', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_admin_2nd_unbind_school():
    sc_info = []
    for sc in School.query.filter_by(admin_id=None).all():
        sc_info.append({
            'id': sc.id,
            'name': sc.name,
            })
    return jsonResponse(sc_info)

# NOTE documnt here
# 3rd_admin ---- get, insert, modify, delete
@adminbp.route('/level1/admin_3rd/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_admin_3rd_list():
    form = GetAdmin3rdListForm()
    if form.validate_on_submit():
        school_id = form.school_id.data
        if school_id is None:
            q1 = Admin.query
        else:
            sc = School.query.get(school_id)
            if not sc:
                return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
            q1 = db.session.query(Admin).\
                    join(Building, Building.admin_id==Admin.id).\
                    join(School, Building.school_id==School.id).\
                    filter(School.id==sc.id)
        ads = []
        for i in q1.all():
            bd = i.building
            if bd:
                bd_info = {
                        'id': bd.id,
                        'name': bd.name,
                        }
                sc_info = {
                        'id': bd.school.id,
                        'name': bd.school.name,
                        }
            else:
                bd_info = None
                sc_info = None
            ads.append({
                'id': i.id,
                'username': i.username,
                'name': i.name,
                'contact_info': i.contact_info,
                'school_info': sc_info,
                'building_info': bd_info,
                })
        return jsonResponse(ads)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/admin_3rd/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_admin_3rd():
    form = CreateAdmin3rdForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        name = form.name.data
        contact_info = form.contact_info.data
        building_id = form.building_id.data
        if Admin.query.filter_by(username=username).count():
            return jsonError(AdminErrno.ADMIN_EXISTS)
        bd = None
        if building_id is not None:
            bd = Building.query.get(building_id)
            if not bd:
                return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
            if bd.admin:
                return jsonError(AdminErrno.BUILDING_BEING_OCCUPIED)
        ad = Admin(
                username=username,
                name=name,
                contact_info=contact_info,
                )
        ad.password = password
        ad.building = bd
        db.session.add(ad)
        db.session.commit()
        bd_info = {
                'id': ad.building.id,
                'name': ad.building.name,
                } if ad.building else None
        sc_info = {
                'id': ad.building.school.id,
                'name': ad.building.school.name,
                } if ad.building else None
        return jsonResponse({
            'id': ad.id,
            'username': ad.username,
            'school_info': sc_info,
            'building_info': bd_info,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/admin_3rd/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_admin_3rd():
    form = ModifyAdmin3rdForm()
    if form.validate_on_submit():
        admin_id = form.admin_id.data
        username = form.username.data
        password = form.password.data
        name = form.name.data
        contact_info = form.contact_info.data
        building_id = form.building_id.data
        ad = Admin.query.get(admin_id)
        if not ad:
            return jsonError(AdminErrno.ADMIN_DOES_NOT_EXIST)
        if ad.username != username:
            if Admin.query.filter_by(username=username).count():
                return jsonError(AdminErrno.USERNAME_EXISTS)
            ad.username = username
        if password:
            ad.password = password
        ad.name = name
        ad.contact_info = contact_info
        if building_id is None:
            ad.building = None
        else:
            bd = Building.query.get(building_id)
            if not bd:
                return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
            if ad.building:
                if ad.building.id == bd.id:
                    pass
                else:
                    if bd.admin:
                        return jsonError(AdminErrno.BUILDING_BEING_OCCUPIED)
                    else:
                        ad.building = bd
            else:
                if bd.admin:
                    return jsonError(AdminErrno.BUILDING_BEING_OCCUPIED)
                else:
                    ad.building = bd
        db.session.add(ad)
        db.session.commit()
        sc_info = {
                'id': bd.school.id,
                'name': bd.school.name,
                } if bd else None
        bd_info = {
                'id': bd.school.id,
                'name': bd.school.name,
                } if bd else None
        return jsonResponse({
            'id': ad.id,
            'username': ad.username,
            'school_info': sc_info,
            'building_info': bd_info,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/admin_3rd/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_admin_3rd():
    form = DeleteAdmin3rdForm()
    if form.validate_on_submit():
        ad_id = form.admin_id.data
        Admin.query.filter_by(id=ad_id).delete()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/admin_3rd/unbind_building', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_admin_3rd_unbind_building():
    form = GetBuildingListForm()
    if form.validate_on_submit():
        sc_id = form.school_id.data
        sc = School.query.get(sc_id)
        if not sc:
            return jsonError(AdminErrno.SCHOOL_DOES_NOT_EXIST)
        bd_info = []
        for bd in sc.buildings.filter_by(admin_id=None).all():
            bd_info.append({
                'id': bd.id,
                'name': bd.name,
                })
        return jsonResponse(bd_info)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

# Cat1 ---- get, insert, modify, delete
@adminbp.route('/level1/cat1/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_cat1_list():
    cat1s = []
    for i in Cat1.query.all():
        cat1s.append({
            'id': i.id,
            'name': i.name,
            })
    return jsonResponse(cat1s)
    
@adminbp.route('/level1/cat1/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_cat1():
    form = CreateCat1Form()
    if form.validate_on_submit():
        name = form.name.data
        if Cat1.query.filter_by(name=name).count():
            return jsonError(AdminErrno.CAT1_EXISTS)
        cat1 = Cat1(name=name)
        db.session.add(cat1)
        db.session.commit()
        return jsonResponse({
            'id': cat1.id,
            'name': cat1.name,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/cat1/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_cat1():
    form = ModifyCat1Form()
    if form.validate_on_submit():
        cat1_id = form.cat1_id.data
        name = form.name.data
        cat1 = Cat1.query.get(cat1_id)
        if not cat1:
            return jsonError(AdminErrno.CAT1_DOES_NOT_EXIST)
        if name == cat1.name:
            pass
        else:
            if Cat1.query.filter_by(name=name).count():
                return jsonError(AdminErrno.CAT1_EXISTS)
        cat1.name = name
        db.session.add(cat1)
        db.session.commit()
        return jsonResponse({
            'id': cat1.id,
            'name': cat1.name,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/cat1/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_cat1():
    form = DeleteCat1Form()
    if form.validate_on_submit():
        Cat1.query.filter_by(id=form.cat1_id.data).delete()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)
     
# Cat2 ---- get, insert, modify, delete
@adminbp.route('/level1/cat2/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_cat2_list():
    form = GetCat2ListForm()
    if form.validate_on_submit():
        cat1_id = form.cat1_id.data
        if cat1_id is None:
            q1 = Cat2.query
        else:
            cat1 = Cat1.query.get(cat1_id)
            if not cat1:
                return jsonError(AdminErrno.CAT1_DOES_NOT_EXIST)
            q1 = cat1.cat2s
        cat2s = []
        for i in q1.all():
            cat2s.append({
                'id': i.id,
                'name': i.name,
                })
        return jsonResponse(cat2s)
    return jsonError(AdminErrno.INVALID_ARGUMENT)
    
@adminbp.route('/level1/cat2/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_cat2():
    form = CreateCat2Form()
    if form.validate_on_submit():
        cat1_id = form.cat1_id.data
        name = form.name.data
        cat1 = Cat1.query.get(cat1_id)
        if not cat1:
            return jsonError(AdminErrno.CAT1_DOES_NOT_EXIST)
        if Cat1.cat2s.filter_by(name=name).count():
            return jsonError(AdminErrno.CAT2_EXISTS)
        cat2 = Cat2(name=name)
        cat2.cat1 = cat1
        db.session.add(cat2)
        db.session.commit()
        return jsonResponse({
            'id': cat2.id,
            'name': cat2.name,
            'cat1_info': {
                'id': cat1.id,
                'name': cat1.name,
                },
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/cat2/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_cat2():
    form = ModifyCat2Form()
    if form.validate_on_submit():
        cat2_id = form.cat2_id.data
        name = form.name.data
        cat2 = Cat2.query.get(cat2_id)
        if not cat2:
            return jsonError(AdminErrno.CAT2_DOES_NOT_EXIST)
        if name == cat2.name:
            pass
        else:
            if Cat2.query.filter_by(name=name):
                return jsonError(AdminErrno.CAT2_EXISTS)
        cat2.name = name
        db.session.add(cat2)
        db.session.commit()
        return jsonResponse({
            'id': cat1.id,
            'name': cat1.name,
            'cat1_info': {
                'id': cat2.cat1.id,
                'name': cat2.cat1.name,
                },
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/cat2/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_cat2():
    form = DeleteCat2Form()
    if form.validate_on_submit():
        Cat2.query.filter_by(id=form.cat2_id.data).delete()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

## product ---- get, insert, modify, delete
@adminbp.route('/level1/product/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_product_list():
    pds = Product.query.order_by(Product.id.desc()).all() 
    pds_info = []
    for pd in pds:
        location_info = []
        pd_bds = pd.product_buildings.all()
        for pd_bd in pd_bds:
            bd = pd_bd.building
            location_info.append({
                'school_info': {
                    'id': bd.school.id,
                    'name': bd.school.name,
                    },
                'building_info': {
                    'id': bd.id,
                    'name': bd.name,
                    },
                'quantity': pd_bd.quantity,
                'timedelta': pd_bd.timedelta,
                })
        pds_info.append({
            'id': pd.id,
            'description': pd.description,
            'img_uri': url_for('static', 'img/'+pd.pic.filename),
            'price': pd.price,
            'cat1_info': {
                'id': pd.cat2.cat1.id,
                'name': pd.cat2.cat1.name,
                },

            'cat2_info': {
                'id': pd.cat2.id,
                'name': pd.cat2.name,
                },
            'asso': location_info,
            })
    return jsonResponse(pds_info)

@adminbp.route('/level1/product/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_product():
    form = CreateProductForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        cat2_id = form.cat2_id.data
        price = form.price.data
        cat2 = Cat2.query.get(cat2_id)
        if not cat2:
            return jsonError(AdminErrno.CAT2_DOES_NOT_EXIST)
        f = savepic(form.img.data)
        p = Product(
                name=name,
                description=description,
                price=price,
                cat2=cat2,
                pic=f,
                )
        db.session.add(f)
        db.session.commit()
        # create initial snapshot
        nf = copypic(p)
        sn = Snapshot(
                product=product,
                name=product.name,
                description=product.description,
                cat1_rd=cat2.cat1.name,
                cat2_rd=cat2.name,
                price=price,
                pic=nf,
                )
        db.session.add(sn)
        db.session.commit()
        return jsonResponse({
            'id': p.id,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/product/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_product():
    form = ModifyProductForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        name = form.name.data
        description = form.description.data
        price = form.price.data
        cat2_id = form.cat2_id.data
        img = form.img.data
        cat2 = Cat2.query.get(cat2_id)
        if not cat2:
            return jsonError(AdminErrno.CAT2_DOES_NOT_EXIST)
        p = Product.query.get(product_id)
        if not p:
            return jsonError(AdminErrno.PRODUCT_DOES_NOT_EXIST)
        if img:
            changepic(p, img)
        p.name = name
        p.description = description
        p.price = price
        p.cat2 = cat2
        db.session.add(p)
        # create a new snapshot
        nf = copypic(p)
        sn = Snapshot(
                name=p.name,
                description=p.description,
                product=p,
                pic=nf,
                cat1_rd=p.cat2.cat1.name,
                cat2_rd=p.cat2.name,
                price=p.price,
                )
        db.session.add(sn)
        db.session.commit()
        return jsonResponse({
            'id': sn.id,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/product/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_product():
    form = DeleteProductForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        p = Product.query.get(product_id)
        if p and p.pic:
            removepic(p.pic.filename)
        db.session.delete(p)
        db.session.commit()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/product/export', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def export_product():
    form = ExportProductForm()
    if form.validate_on_submit():
        pid = form.product_id.data
        pd = Product.query.get(pid)
        if not pd:
            return jsonError(AdminErrno.PRODUCT_DOES_NOT_EXIST)
        items = db.session.query(Order, Order_snapshot, Snapshot).\
                join(Snapshot, Order_snapshot.snapshot_id==Snapshot.id).\
                join(Order, Order_snapshot.order_id==Order.id).\
                filter(Snapshot.product_id==pd.id).\
                order_by(Order.id).all()
        fn = export_product_xls(items, pd.name)
        return jsonResponse(url_for('static', filename='tmp/'+fn)) 
    return jsonError(AdminErrno.INVALID_ARGUMENT)

## product building ---- get, create, modify, delete
@adminbp.route('/level1/associate/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_product_building_list():
    form = GetProductBuildingListForm()
    if form.validate_on_submit():
        pid = form.product_id.data
        pd = Product.query.get(pd)
        if not pd:
            return jsonError(AdminErrno.PRODUCT_DOES_NOT_EXIST)
        pd_bds = pd.product_buildings.all()
        pd_bds_info = []
        for pd_bd in pd_bds:
            bd = pd_bd.building
            pd_bds_info.append({
                'school_info': {
                    'id': bd.school.id,
                    'name': bd.school.name,
                    },
                'building_info': {
                    'id': bd.id,
                    'name': bd.name,
                    },
                'quantity': pd_bd.quantity,
                'timedelta': pd_bd.timedelta,
                }) 
        return jsonResponse(pd_bds_info)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/associate/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_product_building():
    form = CreateProductBuildingForm()
    if form.validate_on_submit():
        p_id = form.product_id.data
        b_id = form.building_id.data
        qty = form.quantity.data
        td = form.timedelta.data
        p = Product.query.get(p_id)
        if not p:
            return jsonError(AdminErrno.PRODUCT_DOES_NOT_EXIST)
        bd = Building.query.get(b_id)
        if not bd:
            return jsonError(AdminErrno.BUILDING_DOES_NOT_EXIST)
        if Product_building.query.filter(product_id==p_id, building_id==b_id).count():
            return jsonError(AdminErrno.PRODUCT_BUILDING_EXISTS)
        pd_bd = Product_building(
                product=p,
                building=bd,
                quantity=qty,
                timedelta=td,
                )
        db,session.add(pd_bd)
        db.session.commit()
        return jsonResponse({
            'product_id': pd_bd.product_id,
            'building_id': pd_bd.building_id,
            'quantity': pd_bd.quantity,
            'timedelta': pd_bd.timedelta,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/associate/modify', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def modify_product_building():
    form = ModifyProductBuildingForm()
    if form.validate_on_submit():
        p_id = form.product_id.data
        b_id = form.building_id.data
        qty = form.quantity.data
        td = form.timedelta.data
        pd_bd = Product_building.query.filter(product_id==p_id, building_id==b_id).first()
        if not pd_bd:
            return jsonError(AdminErrno.PRODUCT_DISASSO_WITH_BUILDING)
        if qty is not None:
            pd_bd.quantity = qty
        pd_bd.timedelta = td
        db.session.add(pd_bd)
        db.session.commit()
        return jsonResponse({
            'product_id': p_id,
            'building_id': b_id,
            'quantity': qty,
            'timedelta': td,
            })
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/associate/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_product_building():
    form = DeleteProductBuildingForm()
    if form.validate_on_submit():
        Product_building.query.filter_by(
                product_id=form.product_id.data,
                building_id=form.building_id.data,
                ).delete()
        db.session.commit()
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

## promotion ---- get, insert, delete
@adminbp.route('/level1/promotion/get_list', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def get_promotion_list():
    pmts = Promotion.query.all()
    pmts_info = []
    for i in pmts:
        f = i.pic
        pmts_info.append({
            'id': i.id,
            'img_uri': url_for('static', filename='img/'+f.filename)
            })
    return jsonResponse(pmts_info)

@adminbp.route('/level1/promotion/create', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def create_promotion():
    form = CreatePromotionForm()
    if form.validate_on_submit():
        file_obj = savepic(form.img.data)
        p = Promotion(pic=f)
        db.session.add(p)
        db.session.commit(p)
        return jsonResponse({'id': p.id})
    return jsonError(AdminErrno.INVALID_ARGUMENT)

@adminbp.route('/level1/promotion/delete', methods=['POST', ])
@admin_login_required(True)
@admin_x_required(1)
@csrf_token_required
def delete_promotion():
    form = DeletePromotionForm()
    if form.validate_on_submit():
        pmt_id = form.promotion_id.data
        pmt = Promotion.query.get(pmt_id)
        if pmt:
            removepic(pmt.pic.filename)  
        return jsonResponse(None)
    return jsonError(AdminErrno.INVALID_ARGUMENT)

def _get_time_():
    return datetime.datetime.now()-datetime.timedelta(days=30)

