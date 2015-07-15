# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

class CreateCartForm(Form):
    product_id = IntegerField(validators=[Required(), ])
    quantity = IntegerField(validators=[Required(), ])
    def validate_quantity(form, field):
        if field.data <= 0:
            raise ValidationError('Quantity Must be positive.')

class CartForm(Form):
    product_id = IntegerField(validators=[Required(), ])

class SetCartForm(Form):
    product_id = IntegerField(validators=[Required(), ])
    quantity = IntegerField(validators=[Required(), ])
    def validate_quantity(form, field):
        if field.data <= 0:
            raise ValidationError('Quantity must be positive.')
