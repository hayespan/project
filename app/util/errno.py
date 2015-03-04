# -*- coding: utf-8 -*-

# global errno
class Errno(object):
    INVALID_ARGUMENT = (1, 'Invalid arguments.')
    CSRF_FAILED = (2, 'Csrf token check failed.')

# custom errno
class UserErrno(Errno):
    BUILDING_DOES_NOT_EXIST = (-1, 'Building does not exist.')
    USER_OFFLINE = (-2, 'User should choose location to init account.')
    LOCATION_INFO_DOES_NOT_EXIST = (-3, 'Location info does not exist.')
    CONTACT_INFO_DOES_NOT_EXIST = (-4, 'Contact info does not exist.')

class AdminErrno(Errno):
    pass

class FileErrno(Errno):
    pass

class CartErrno(Errno):
    pass

class ProductErrno(Errno):
    pass

class LocationErrno(Errno):
    pass

class OrderErrno(Errno):
    pass

class CategoryErrno(Errno):
    pass

