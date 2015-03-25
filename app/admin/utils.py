# -*- coding: utf-8 -*-
import os
from hashlib import md5
from functools import wraps

from flask import session, g, redirect, url_for

from .models import Admin

from ..util.errno import AdminErrno
from ..util.common import jsonError
from ..location.models import Building

def admin_login_required(api, view_path=None):
    '''
    api: True if ajax else False
    '''
    def _admin_login_required(func):
        '''admin login required decorator'''
        @wraps(func)
        def _wrapped(*args, **kwargs):
            adminid = session.get('admin_id')
            _csrf_token = session.get('admin_csrf_token')
            if not (adminid and _csrf_token and Admin.query.filter_by(id=adminid).count()):
                if api:
                    return jsonError(AdminErrno.ADMIN_OFFLINE)
                else:
                    return redirect(url_for(view_path))
            g.admin = Admin.query.filter_by(id=adminid).first()
            return func(*args, **kwargs)
        return _wrapped
    return _admin_login_required

def admin_x_required(privilege):
    '''privilege: 1, 2, 4
    '''
    def _admin_x_required(func):
        '''permission decorator
        '''
        @wraps(func)
        def _wrapped(*args, **kwargs):
            admin = g.admin
            if admin.privilege == privilege:
                return func(*args, **kwargs)
            return jsonError(AdminErrno.PERMISSION_DENIED)
        return _wrapped
    return _admin_x_required

# get the total sales of an order
def get_order_money(order):
    money = 0
    order_snapshots = order.order_snapshots.all()
    for order_snapshot in order_snapshots:
        money = money + float(order_snapshot.snapshot.price) * int(order_snapshot.quantity)
    return money

# judge if the month is in the quarter
# 1, 2, 3    -> 1
# 4, 5, 6    -> 2
# 7, 8, 9    -> 3
# 10, 11, 12 -> 4
def is_in_same_quarter(month, quarter):
    return quarter == (month / 4 + 1)

def is_in_same_month(m1, m2):
    return (m2 == 'all') or (m1 == int(m2))

def parse_quarter_2_month(x):
    '''parse quarter to month list
    '''
    t = (x-1)%4+1
    return [t*3-2, t*3-1, t*3]
