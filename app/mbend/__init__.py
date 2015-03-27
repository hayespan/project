# -*- coding: utf-8 -*-
from flask import Blueprint

mobilebp = Blueprint(
        'mbend',
        __name__,
        # if templates & static dirs are in
        # subapp/ then the following configs
        # are needed.
        # template_folder='templates',
        # static_folder='static'.
        )

from . import views 
