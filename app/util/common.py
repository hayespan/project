# -*- coding: utf-8 -*-
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

