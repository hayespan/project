# -*- coding: utf-8 -*-
import re
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

mobile_p = re.compile(r'^(0?(13[0-9]|15[012356789]|18[0236789]|14[57])[0-9]{8})$')
telephone_p = re.compile(r'^((?:\d{2,5}-)?\d{7,8}(?:-\d{1,})?)$')
product_ids_p = re.compile(r',?((?:\d+,)*\d+),?')

class CreateOrderForm(Form):
    product_ids = StringField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(1, 15)])
    phone = StringField(validators=[Required(), ]) 
    addr = StringField(validators=[Required(), Length(1, 100)])

    def validate_product_ids(form ,field):
        ids = re.findall(product_ids_p, field.data)
        if ids:
            form.product_ids_list = ids[0].split(',')
        else:
            raise ValidationError('Product ids format error.')
    def validate_phone(form, field):
        if not (re.match(mobile_p, field.data) or\
                re.match(telephone_p, field.data)):
            raise ValidationError('Not a telephone or mobile phone number.')



