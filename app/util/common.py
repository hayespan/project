# -*- coding: utf-8 -*-
from flask import jsonify

def jsonError(ERROR):
    return jsonify({'code': ERROR[0], 'data': ERROR[1]})

def jsonResponse(data):
    return jsonify({'code': 0, 'data': data})
