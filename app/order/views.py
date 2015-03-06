# -*- coding: utf-8 -*-
from flask import g 

from . import orderbp
from .models import Order, Order_snapshot
from .forms import *

from .. import db
from ..util.common import jsonResponse, jsonError, viaMobile
from ..util.errno import OrderErrno
from ..util.csrf import csrf_token_required
from ..user.utils import buyer_login_required


# ajax
def create_order():
    pass

def get_order_list():
    pass

