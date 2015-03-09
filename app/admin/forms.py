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

class ModifyQuantityForm(Form):
    building_id = IntegerField(validators=[Required(), ])
    producct_id = IntegerField(validators=[Required(), ])
    quantity = IntegerField(validators=[Required(), ])

class CreateSchoolForm(Form):
    name = StringField(validators=[Required(), Length(1, 32), ])

class ModifySchoolForm(CreateSchoolForm):
    school_id = IntegerField(validators=[Required(), ])

class DeleteSchoolForm(Form):
    school_id = IntegerField(validators=[Required(), ])

class GetBuildingListForm(Form):
    school_id = IntegerField(validators=[Required(), ])

class CreateBuildingForm(Form):
    school_id = IntegerField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(1, 32), ])

class ModifyBuildingForm(Form):
    building_id = IntegerField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(1, 32), ])

class DeleteBuildingForm(Form):
    building_id = IntegerField(validators=[Required(), ])

class CreateAdmin2ndForm(Form):
    username = StringField(validators=[Required(), Length(1, 32)])
    password = PasswordField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(0, 32), ])
    contact_info = StringField(validators=[Required(), Length(0, 100), ])
    school_id = IntegerField(validators=[Optional(), ])

class ModifyAdmin2ndForm(Form):
    admin_id = IntegerField(validators=[Required(), ])
    username = StringField(validators=[Required(), Length(1, 32)])
    password = PasswordField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(0, 32), ])
    contact_info = StringField(validators=[Required(), Length(0, 100), ])
    school_id = IntegerField(validators=[Optional(), ])

class DeleteAdmin2ndForm(Form):
    admin_id = IntegerField(validators=[Required(), ])

class CreateCat1Form(Form):
    name = StringField(validators=[Required(), Length(1, 32), ])

class ModifyCat1Form(CreateCat1Form):
    cat1_id = IntegerField(validators=[Required(), ])

class DeleteCat1Form(Form):
    cat1_id = IntegerField(validators=[Required(), ])
