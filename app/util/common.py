# -*- coding: utf-8 -*-
import time
import datetime 
from flask import jsonify, request, redirect
from functools import wraps

def jsonError(ERROR):
    return jsonify({'code': ERROR[0], 'data': ERROR[1]})

def jsonResponse(data):
    return jsonify({'code': 0, 'data': data})

USERAGENT = ('micromessenger', 'Mobile', 'iPhone', 'Windows Phone', 'UCWEB', 'Fennec', 'Opera Mobi', 'BlackBerry', )

def viaMobile():
    s = request.headers.get('User-Agent')
    if s is None:
        return False
    for i in USERAGENT:
        if i in s:
            return True
    return False

def PC_MB_distribute(url):
    '''pc and mobile end distribution'''
    def _PC_MB_distribute(func):
        @wraps(func) 
        def _wrap(*args, **kwargs):
            if viaMobile():
                return redirect(url)
            return func(*args, **kwargs)
        return _wrap
    return _PC_MB_distribute

def datetime_2_unixstamp(dt):
    '''datetime obj parsed to unixstamp
    '''
    return time.mktime(dt.timetuple())

def timedelta_2_second(hours_f):
    '''floating type, hour-delta, parsed to seconds
    '''
    return datetime.timedelta(hours=float(hours_f)).seconds
