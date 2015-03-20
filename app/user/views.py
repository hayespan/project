# -*- coding: utf-8 -*-

import os

from flask import session, g, request
from hashlib import md5

from . import userbp
from .models import User
from .forms import CreateUserForm
from .utils import buyer_login_required

from .. import db
from ..util.common import jsonError, jsonResponse
from ..util.errno import UserErrno
from ..util.csrf import init_csrf_token, csrf_token_required
from ..location.models import Building 

# ajax
@userbp.route('/choose_location', methods=['POST', ])
def choose_location():
    form = CreateUserForm()    
    if form.validate_on_submit():
        bd = Building.query.filter_by(id=form.building_id.data).first()
        if not bd:
            return jsonError(UserErrno.BUILDING_DOES_NOT_EXIST)
        uid = session.get('buyerid')
        if uid:
            u = User.query.get(uid)
        else:
            u = User()
            db.session.add(u)
            db.session.commit()
            session['buyerid'] = u.id
        init_csrf_token()
        sc = bd.school
        session['buyer_location_info'] = ((sc.id, sc.name), (bd.id, bd.name))
        return jsonResponse({'_csrf_token': session['_csrf_token']})
    return jsonError(UserErrno.INVALID_ARGUMENT)

# ajax
@userbp.route('/location_info', methods=['POST', ])
@buyer_login_required(True)
@csrf_token_required
def get_user_location_info():
    data = session.get('buyer_location_info')
    if not data:
        return jsonError(UserErrno.LOCATION_INFO_DOES_NOT_EXIST)
    return jsonResponse({'school': {'id': data[0][0], 'name': data[0][1]}, 'building': {'id': data[1][0], 'name': data[1][1]} })


# ajax
@userbp.route('/contact_info', methods=['POST', ])
@buyer_login_required(True)
@csrf_token_required
def profile():
    data = session.get('buyer_contact_info')
    if not data:
        return jsonError(UserErrno.CONTACT_INFO_DOES_NOT_EXIST)
    return jsonResponse({'name': data[0], 'phone': data[1], 'addr': data[2]})

