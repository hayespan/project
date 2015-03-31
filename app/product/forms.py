# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

class CatxPageForm(Form):
    cat1_id = IntegerField(validators=[Optional(), ])
    cat2_id = IntegerField(validators=[Optional(), ])
    # page = IntegerField(validators=[Optional(), ])

class GetHotProductList(Form):
    delta = IntegerField(validators=[Optional(), ])
