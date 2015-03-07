# -*- coding: utf-8 -*-
<<<<<<< HEAD
from flask import session, g
from functools import wraps

from .models import Admin

from ..util.errno import AdminErrno
from ..util.common import jsonError
from ..location.models import Building

def admin_login_required(func):
    '''admin login required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            adminid = session['admin_id']
            _csrf_token = session['_csrf_token']
            privilege = session['admin_privilege']
            username = session['admin_username']
        except Exception as e:
            return jsonError(AdminErrno.ADMIN_OFFLINE)
        else:
            if not (adminid and _csrf_token and privilege and username):
                return jsonError(AdminErrno.ADMIN_OFFLINE)
        g.admin = Admin.query.filter_by(id=adminid).first()
        return func(*args, **kwargs)
    return _wrapped

# get the total sales of an order
def get_order_money(order):
    money = 0
    snapshots = order.order_snapshots
    for snapshot in snapshots:
        money = money + float(Snapshot.query.filter_by(id = snapshot.snapshot_id).first().price) * int(snapshot.quantity)
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
=======

from functools import wraps
from flask import abort
from flask.ext.login import current_user

def root_required(func):
    '''
    root required decorator
    '''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        if current_user.is_root:
            return func(*args, **kwargs)
        return abort(404)
    return _wrapped
>>>>>>> dev0
