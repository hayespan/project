# -*- coding: utf-8 -*-
from .models import Cat1, Cat2

def _get_catx():
    return [[i, i.cat2s.order_by(Cat2.id).all()] for i in Cat1.query.order_by(Cat1.id).all()]

