# -*- coding: utf-8 -*-
from . import adminbp 

@adminbp.route('/')
def index():
    return 'hello world'
