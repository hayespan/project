# -*- coding: utf-8 -*-

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
