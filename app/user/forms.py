# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

class CreateUserForm(Form):
    building_id = IntegerField(validators=[Required(), ])

