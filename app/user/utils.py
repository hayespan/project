# -*- coding: utf-8 -*-
from flask import session, g
from functools import wraps

from .models import User
from ..util.errno import UserErrno

def buyer_login_required(func):
    '''buyer login required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        userid = session['buyerid']
        _csrf_token = session['_csrf_token']
        buyer_location_info = session['buyer_location_info']
        if not (userid and _csrf_token and buyer_location_info):
            return jsonError(UserErrno.USER_OFFLINE)
        g.buyer = User.query.filter_by(id=userid).first()
        return func(*args, **kwargs)
    return _wrapped
