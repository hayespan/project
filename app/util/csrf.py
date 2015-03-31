# -*- coding: utf-8 -*-
from flask import request
import os
from hashlib import md5
from functools import wraps
from flask import session
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

from .common import jsonError
from .errno import Errno

def init_admin_csrf_token():
    session['admin_csrf_token'] = md5(os.urandom(64)).hexdigest()

def init_csrf_token():
    session['_csrf_token'] = md5(os.urandom(64)).hexdigest()

class CsrfTokenForm(Form):
    csrf_token = StringField(_name='csrf_token', validators=[Required(), Length(min=32, max=32), ])

def csrf_token_required(func):
    '''check csrf token required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        form = CsrfTokenForm()
        if form.validate_on_submit():
            csrf = form.csrf_token.data
            if csrf == session.get('_csrf_token', None):
                return func(*args, **kwargs)
        return jsonError(Errno.CSRF_FAILED)
    return _wrapped

def admin_csrf_token_required(func):
    '''check csrf token required decorator'''
    @wraps(func)
    def _wrapped(*args, **kwargs):
        form = CsrfTokenForm()
        if form.validate_on_submit():
            csrf = form.csrf_token.data
            if csrf == session.get('admin_csrf_token', None):
                return func(*args, **kwargs)
        return jsonError(Errno.CSRF_FAILED)
    return _wrapped
