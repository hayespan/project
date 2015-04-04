# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import TextAreaField, StringField, BooleanField, DateField, IntegerField, PasswordField, DecimalField
from wtforms.validators import Required, Length, Optional, ValidationError, Regexp

class LoginForm(Form):
    username = StringField(validators=[Required(), Length(1, 64), ])
    password = PasswordField(validators=[Required(), ])

class HandleOrderForm(Form):
    ticketid = StringField(validators=[Required(), Length(20, 20), ])
    password = StringField(validators=[Required(), Length(4, 4), ])
    handle = IntegerField(validators=[Required(), ])

class ModifyQuantityForm(Form):
    building_id = IntegerField(validators=[Required(), ])
    product_id = IntegerField(validators=[Required(), ])
    quantity = IntegerField(validators=[Required(), ])

class AdminLevel2Form(Form):
    get_building_list = IntegerField(validators=[Optional(), ])
    get_order_list = IntegerField(validators=[Optional(), ])
    get_inventory_list = IntegerField(validators=[Optional(), ])
    get_total_sales = IntegerField(validators=[Optional(), ])

class AdminLevel3Form(Form):
    get_order_list = IntegerField(validators=[Optional(), ])
    get_inventory_list = IntegerField(validators=[Optional(), ])

class GetTotalSalesForm(Form):
    school_id = IntegerField(validators=[Optional(), ])
    building_id = IntegerField(validators=[Optional(), ])
    year = IntegerField(validators=[Optional(), ])
    quarter = IntegerField(validators=[Optional(), ])
    month = IntegerField(validators=[Optional(), ])
    export = IntegerField(validators=[Optional(), ])

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
    password = PasswordField(validators=[Optional(), ])
    name = StringField(validators=[Required(), Length(0, 32), ])
    contact_info = StringField(validators=[Required(), Length(0, 100), ])
    school_id = IntegerField(validators=[Optional(), ])

class DeleteAdmin2ndForm(Form):
    admin_id = IntegerField(validators=[Required(), ])

class GetAdmin3rdListForm(Form):
    school_id = IntegerField(validators=[Optional(), ])

class CreateAdmin3rdForm(Form):
    username = StringField(validators=[Required(), Length(1, 32)])
    password = PasswordField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(0, 32), ])
    contact_info = StringField(validators=[Required(), Length(0, 100), ])
    building_id = IntegerField(validators=[Optional(), ])

class ModifyAdmin3rdForm(Form):
    admin_id = IntegerField(validators=[Required(), ])
    username = StringField(validators=[Required(), Length(1, 32)])
    password = PasswordField(validators=[Optional(), ])
    name = StringField(validators=[Required(), Length(0, 32), ])
    contact_info = StringField(validators=[Required(), Length(0, 100), ])
    building_id = IntegerField(validators=[Optional(), ])

class DeleteAdmin3rdForm(Form):
    admin_id = IntegerField(validators=[Required(), ])

class CreateCat1Form(Form):
    name = StringField(validators=[Required(), Length(1, 32), ])

class ModifyCat1Form(CreateCat1Form):
    cat1_id = IntegerField(validators=[Required(), ])

class DeleteCat1Form(Form):
    cat1_id = IntegerField(validators=[Required(), ])

class GetCat2ListForm(Form):
    cat1_id = IntegerField(validators=[Optional(), ])
    
class CreateCat2Form(Form):
    cat1_id = IntegerField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(1, 32), ])

class ModifyCat2Form(CreateCat1Form):
    cat2_id = IntegerField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(1, 32), ])

class DeleteCat2Form(Form):
    cat2_id = IntegerField(validators=[Required(), ])

class CreateProductForm(Form):
    name = StringField(validators=[Required(), Length(1, 50), ])
    description = StringField(validators=[Required(), ])
    cat2_id = IntegerField(validators=[Required(), ])
    price = DecimalField(validators=[Required(), ]) 
    img = FileField(validators=[FileRequired(), ])

class ModifyProductForm(Form):
    product_id = IntegerField(validators=[Required(), ])
    name = StringField(validators=[Required(), Length(1, 50), ])
    description = StringField(validators=[Required(), ])
    cat2_id = IntegerField(validators=[Required(), ])
    price = DecimalField(validators=[Required(), ]) 
    img = FileField(validators=[Optional(), ])

class DeleteProductForm(Form):
    product_id = IntegerField(validators=[Required(), ])

class ExportProductForm(Form):
    product_id = IntegerField(validators=[Required(), ])

class GetProductBuildingListForm(Form):
    product_id = IntegerField(validators=[Required(), ])

class CreateProductBuildingForm(Form):
    product_id = IntegerField(validators=[Required(), ])
    school_id = IntegerField(validators=[Optional(), ])
    building_id = IntegerField(validators=[Optional(), ])
    quantity = IntegerField(validators=[Optional(), ])
    timedelta = DecimalField(validators=[Optional(), ])

class ModifyProductBuildingForm(Form):
    product_id = IntegerField(validators=[Required(), ])
    building_id = IntegerField(validators=[Required(), ])
    quantity = IntegerField(validators=[Optional(), ])
    timedelta = DecimalField(validators=[Required(), ])

class DeleteProductBuildingForm(Form):
    product_id = IntegerField(validators=[Required(), ])
    building_id = IntegerField(validators=[Required(), ])

class CreatePromotionForm(Form):
    img = FileField(validators=[FileRequired(), ])

class DeletePromotionForm(Form):
    promotion_id = IntegerField(validators=[Required(), ])

