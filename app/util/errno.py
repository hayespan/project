# -*- coding: utf-8 -*-

# global errno
class Errno(object):
    INVALID_ARGUMENT = (1, 'Invalid arguments.')

# custom errno
class UserErrno(Errno):
    BUILDING_DOES_NOT_EXIST = (-1, 'Building does not exist.')

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

