# -*- coding: utf-8 -*-
import time
import datetime 
from flask import jsonify, request

def jsonError(ERROR):
    return jsonify({'code': ERROR[0], 'data': ERROR[1]})

def jsonResponse(data):
    return jsonify({'code': 0, 'data': data})

def viaMobile():
    s = request.headers.get('User-Agent')
    kw = ['micromessenger', 'Mobile', 'iPhone', 'Windows Phone', 'UCWEB', 'Fennec', 'Opera Mobi', 'BlackBerry', ]
    for i in kw:
        if i in s:
            return True
    return False

def datetime_2_unixstamp(dt):
    '''datetime obj parsed to unixstamp
    '''
    return time.mktime(dt.timetuple())

def timedelta_2_second(hours_f):
    '''floating type, hour-delta, parsed to seconds
    '''
    return datetime.timedelta(hours=float(hours_f)).seconds
