# -*- coding: utf-8 -*-
from flask import session, g
from functools import wraps

from .models import User
from ..util.errno import UserErrno

def buyer_login_required(func):
    '''buyer login required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        userid = session.get('buyerid')
        _csrf_token = session.get('_csrf_token')
        buyer_location_info = session.get('buyer_location_info')
        buyer_contact_info = session.get('buyer_contact_info')
        if not (userid and _csrf_token and buyer_location_info):
            return jsonError(UserErrno.USER_OFFLINE)
        buyer = User.query.filter_by(id=userid).first()
        buyer.location_info = {
                'school_id': buyer_location_info[0][0],
                'school_name': buyer_location_info[0][1],
                'building_id': buyer_location_info[1][0],
                'building_name': buyer_location_info[1][1],
                }
        buyer.csrf_token = _csrf_token
        if buyer_contact_info:
            buyer.name = buyer_contact_info[0]
            buyer.mobile = buyer_contact_info[1]
            buyer.addr = buyer_contact_info[2]
        g.buyer = buyer
        return func(*args, **kwargs)
    return _wrapped
