# -*- coding: utf-8 -*-

# global errno
class Errno(object):
    INVALID_ARGUMENT = (1, 'Invalid arguments.')
    CSRF_FAILED = (2, 'Csrf token check failed.')
    USER_OFFLINE = (3, 'User should choose location to init account.')

# custom errno
class UserErrno(Errno):
    BUILDING_DOES_NOT_EXIST = (-1, 'Building does not exist.')
    LOCATION_INFO_DOES_NOT_EXIST = (-2, 'Location info does not exist.')
    CONTACT_INFO_DOES_NOT_EXIST = (-3, 'Contact info does not exist.')

class AdminErrno(Errno):
    PRIVILEGE_ILLEGAL = (-1, 'The privilege of current admin is illegal.')
    ADMIN_OFFLINE = (-2, 'Admin didn\'t login.')
    BUILDING_DOES_NOT_EXIST = (-3, 'Building does not exist.')
    TIME_ILLEGAL = (-4, 'The time provided by front-end is illegal.')
    NOT_ENOUGH_ARGS = (-5, 'The amount of args is not enough.')
    NO_BUILDING_IN_CHARGE = (-6, 'This administrator has no building in charge.')
    ADMIN_DOES_NOT_EXIST = (-7, 'Admin account does not exist.')
    AUTHENTICATION_FAILED = (-8, 'Authentication failed.')
    NO_SCHOOL_IN_CHARGE = (-9, 'This administrator has no school in charge.')
    PERMISSION_DENIED = (-10, 'Act beyond authority.')

class FileErrno(Errno):
    pass

class CartErrno(Errno):
    MUST_CLEAR_CART = (-1, 'Your cart has products not in your current location. Should Clear first.')
    CART_INVALID = (-2, 'Product does not exist or quantity is 0.')
    CART_DOES_NOT_EXIST = (-3, 'Cart record does not exist.')

class ProductErrno(Errno):
    CATX_DOES_NOT_EXIST = (-1, 'Category x does not exist.')

class LocationErrno(Errno):
    SCHOOL_DOES_NOT_EXIST = (-1, 'School does not exist.')

class OrderErrno(Errno):
    PRODUCT_REFRESH = (-1, 'Some product info has been updated, please reload.')
    CART_INVALID = (-2, 'Some item in cart is invalid, please reload.')

class CategoryErrno(Errno):
    pass

