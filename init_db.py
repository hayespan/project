#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import App, db
app = App()

from app.admin.models import *
from app.cart.models import *
from app.category.models import *
from app.location.models import *
from app.order.models import *
from app.product.models import *
from app.user.models import *

with app.app.app_context():
    db.create_all()
