# -*- coding: utf-8 -*-
import os
from hashlib import md5
from flask import session, g, redirect, url_for
from functools import wraps

from .models import User
from ..util.errno import UserErrno
from ..util.common import jsonError, viaMobile
from ..location.models import Building 
from .. import db

def buyer_login_required(api, view_path=None):
    '''buyer login required decorator for api
    api: True/False
    '''
    def _buyer_login_required(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            userid = session.get('buyerid')
            _csrf_token = session.get('_csrf_token')
            buyer_location_info = session.get('buyer_location_info')
            buyer_contact_info = session.get('buyer_contact_info')
            if not (userid and _csrf_token and buyer_location_info and db.session.query(Building).filter(Building.id==buyer_location_info[1][0]).count()):
                if api:
                    return jsonError(UserErrno.USER_OFFLINE)
                else:
                    return redirect(url_for(view_path))
            buyer = User.query.filter_by(id=userid).first()
            buyer.location_info = {
                    'school_id': buyer_location_info[0][0],
                    'school_name': buyer_location_info[0][1],
                    'building_id': buyer_location_info[1][0],
                    'building_name': buyer_location_info[1][1],
                    }
            buyer.building = db.session.query(Building).filter(Building.id==buyer_location_info[1][0]).first()
            buyer.csrf_token = _csrf_token
            if buyer_contact_info:
                buyer.name = buyer_contact_info[0]
                buyer.mobile = buyer_contact_info[1]
                buyer.addr = buyer_contact_info[2]
            else:
                buyer.name = u'匿名用户'
            g.buyer = buyer
            return func(*args, **kwargs)
        return _wrapped
    return _buyer_login_required
