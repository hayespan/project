# -*- coding: utf-8 -*-
from datetime import datetime
from flask import g 

from . import cartbp
from .models import Cart
from .forms import CreateCartForm, CartForm 

from .. import db
from ..util.common import jsonResponse, jsonError, viaMobile
from ..util.csrf import csrf_token_required
from ..util.errno import CartErrno
from ..user.utils import buyer_login_required
from ..product.models import Product

# ajax
@cartbp.route('/cnt', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def get_cart_num():
    u = g.buyer
    return jsonResponse(u.carts.count())


# ajax
@cartbp.route('/insert', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def create_cart():
    u = g.buyer
    if u.carts.filter(Cart.building_id!=u.location_info['building_id']).count():
        return jsonError(CartErrno.MUST_CLEAR_CART)
    form = CreateCartForm()
    if form.validate_on_submit():
        pd = Product.query.filter_by(id=form.product_id.data).first()
        if not pd: #1 building does not exist, failed
            return jsonError(CartErrno.CART_INVALID)
        quantity = form.quantity.data
        pd_bd = pd.product_buildings.filter(Product_building.building_id==u.location_info['building_id']).first()
        if not pd_bd: #2 product detached from building, failed. 
            return jsonError(CartErrno.CART_INVALID)
        pd_quantity = pd_bd.quantity
        if pd_quantity == 0: # product sold out, failed.
            return jsonError(CartErrno.CART_INVALID)
        # check whether cart obj exists
        cart =  u.carts.filter(Cart.product_id==pd.id).first()
        if cart:
            if pd_quantity < cart.quantity + quantity:
                quantity = pd_quantity
            else:
                quantity = cart.quantity + quantity
            cart.quantity = quantity
        else:
            if pd_quantity < quantity:
                quantity = pd_quantity
            cart = Cart(
                    user=u,
                    building_id=u.location_info['building_id'],
                    product=pd,
                    quantity=quantity,
                    )
        db.session.add(cart)
        db.commit()
        return jsonResponse(cart.id)
    return jsonError(CartErrno.INVALID_ARGUMENT)
    
# ajax
@cartbp.route('/', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def get_cart_list():
    u = g.buyer
    carts = u.carts.all()
    items = []
    for i in carts:
        pb =  i.product.product_buildings.filter(Product_building.building_id==u.location_info['building_id']).first()
        if not pb:
            pb.is_valid = False
        if pb.quantity == 0:
            pb.is_valid = False
        if pb.quantity<i.quantity:
            i.quantity = pb.quantity
        i.last_viewed_time = datetime.now()
        db.session.add(i)
        pd = i.product
        items.append({
            'product_id': pd.id,
            'name': pd.name,
            'description': pd.description,
            'filename': pd.pic.filename,
            'price': pd.price,
            'quantity': i.quantity,
            'is_valid': i.is_valid,
            })
    db.session.commit()
    return jsonResponse(items)

# ajax
@cartbp.route('/add', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def increase_cart_quantity():
    u = g.buyer
    form = CartForm()
    if form.validate_on_submit():
        cart = db.session.query(Cart).filter(Cart.user_id==u.id, Cart.building_id==u.location_info['building_id'], Cart.product_id==form.product_id.data).first()
        if not cart:
            return jsonError(CartErrno.CART_DOES_NOT_EXIST)
        pb = db.session.query(Product_building).filter(Product_building.building_id==u.location_info['building_id'], Product_building.product_id==product_id).first()
        if not pb or pb.quantity == 0:
            cart.is_valid = False
            db.session.add(cart)
            db.session.commit()
            return jsonError(CartErrno.CART_INVALID)
        qty = cart.quantity+1
        if qty>pb.quantity:
            qty = pb.quantity
        cart.quantity = qty
        db.session.add(cart)
        db.session.commit()
        return jsonResponse(cart.quantity)
    return jsonError(CartErrno.INVALID_ARGUMENT)

#ajax
@cartbp.route('/sub', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def decrease_cart_quantity():
    u = g.buyer
    form = CartForm()
    if form.validate_on_submit():
        cart = db.session.query(Cart).filter(Cart.user_id==u.id, Cart.building_id==u.location_info['building_id'], Cart.product_id==form.product_id.data).first()
        if not cart:
            return jsonError(CartErrno.CART_DOES_NOT_EXIST)
        pb = db.session.query(Product_building).filter(Product_building.building_id==u.location_info['building_id'], Product_building.product_id==product_id).first()
        if not pb or pb.quantity == 0:
            cart.is_valid = False
            db.session.add(cart)
            db.session.commit()
            return jsonError(CartErrno.CART_INVALID)
        qty = cart.quantity-1 or 1
        if qty>pb.quantity:
            qty = pb.quantity
        cart.quantity = qty
        db.session.add(cart)
        db.session.commit()
        return jsonResponse(cart.quantity)
    return jsonError(CartErrno.INVALID_ARGUMENT)

# ajax
@cartbp.route('/delete', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def delete_cart():
    u = g.buyer
    form = CartForm()
    if form.validate_on_submit():
        cart = u.carts.filter_by(product_id=form.product_id.data).first()
        if cart:
            db.session.delete(cart)
            db.session.commit()
        return jsonResponse(None)
    return jsonError(CartErrno.INVALID_ARGUMENT)

#ajax
@cartbp.route('/clear', methods=['POST', ])
@buyer_login_required
@csrf_token_required
def clear_cart():
    u = g.buyer
    db.session.delete(u.carts)
    return jsonResponse(None)

