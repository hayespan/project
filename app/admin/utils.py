# -*- coding: utf-8 -*-
from flask import session, g
from functools import wraps

from .models import Admin
from ..util.errno import AdminErrno

def admin_login_required(func):
    '''admin login required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        adminid = session['admin_id']
        _csrf_token = session['_csrf_token']
        privilege = session['admin_privilege']
        username = session['admin_username']
        if not (adminid and _csrf_token and privilege and username)
            return jsonError(AdminErrno.ADMIN_OFFLINE)
        g.admin = Admin.query.filter_by(id=adminid).first()
        return func(*args, **kwargs)
    return _wrapped

