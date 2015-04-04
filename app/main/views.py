# -*- coding: utf-8 -*-

from flask import session, render_template, url_for

from . import mainbp
from .. import db
from ..user.models import User
from ..category.models import Cat1, Cat2
from ..product.models import Product, Product_building
from ..pic.models import Promotion
from ..util.common import viaMobile
from ..category.utils import _get_catx
from ..location.models import School, Building
from ..util.common import PC_MB_distribute

@mainbp.route('/', methods=['GET', ])
@PC_MB_distribute('/m/')
def index():
    uid = session.get('buyerid')
    user = User.query.filter_by(id=uid).first() if uid else None
    if user:
        buyer_contact_info = session.get('buyer_contact_info')
        if buyer_contact_info:
            user.name = buyer_contact_info[0]
        else:
            user.name = u'匿名用户'
        buyer_location_info = session.get('buyer_location_info')
        user.location_info = {
                'school_id': buyer_location_info[0][0],
                'school_name': buyer_location_info[0][1],
                'building_id': buyer_location_info[1][0],
                'building_name': buyer_location_info[1][1],
                }
    schools = School.query.all()
    locations = [[i, i.buildings.all()] for i in schools]
    if user:
        hot_products = db.session.query(Product, Product_building.sold_cnt_rd, Product_building.quantity).\
                join(Product_building, Product_building.product_id==Product.id).\
                filter(Product_building.building_id==session['buyer_location_info'][1][0]).\
                order_by(db.desc(db.case([
                    (Product_building.quantity!=0, Product_building.sold_cnt_rd),
                    (Product_building.quantity==0, -1)]))).\
                limit(10).\
                all()
    else:
        hot_products = db.session.query(
                Product, db.func.sum(Product_building.sold_cnt_rd).label('tot_sold_cnt'), db.func.sum(Product_building.quantity)).\
                join(Product_building, Product_building.product_id==Product.id).\
                group_by(Product.id).\
                order_by(db.desc('tot_sold_cnt')).\
                limit(10).\
                all()
    promotions = [i.pic.filename for i in Promotion.query.all()]
    return render_template('pc/main_page.html', user=user, catx=_get_catx(), hot_products=hot_products, promotions=promotions, locations=locations)

