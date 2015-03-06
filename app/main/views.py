# -*- coding: utf-8 -*-

from flask import session, render_template

from . import mainbp
from .. import db
from ..user.models import User
from ..category.models import Cat1, Cat2
from ..product.models import Product, Product_building
from ..pic.models import Promotion
from ..util.common import viaMobile

@mainbp.route('/', methods=['GET', ])
def index():
    uid = session.get('buyerid')
    user = User.query.filter_by(id=uid).first() if uid else None
    if not session.get('buyer_contact_info'):
        session['buyer_contact_info'] = [u'匿名用户', '', '']
    if user:
        user.name = session['buyer_contact_info'][0]
    catx = [[i, [j for j in i.cat2s.order_by(Cat2.id.desc()).all()]] for i in Cat1.query.order_by(Cat1.id.asec()).all()]
    if user:
        hot_products = db.session.query(Product, Product_building.sold_cnt_rd, Product_building.quantity).\
                join(Product_building, Product_building.product_id==Product.id).\
                filter(Product_building.building_id==session['buyer_location_info'][1][0]).\
                order_by(db.desc(db.case([
                    (Product_building.quantity!=0, Product_building.sold_cnt_rd),
                    (Product_building.quantity==0, 0)]))).\
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
    if viaMobile():
        return render_template('', user=user, catx=catx, hot_products=hot_products, promotions=promotions)
    else: 
        return render_template('', user=user, catx=catx, hot_products=hot_products, promotions=promotions)


    
    

