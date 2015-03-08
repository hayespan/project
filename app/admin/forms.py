# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField, PasswordField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

class LoginForm(Form):
    username = StringField(validators=[Required(), Length(1, 64), ])
    password = PasswordField(validators=[Required(), ])

class HandleOrderForm(Form):
    ticketid = StringField(validators=[Required(), Length(1, 21), ])
    password = PasswordField(validators=[Required(), ])
    handle = BooleanField(validators=[Required(), ])

