# -*- coding: utf-8 -*-
import os
from hashlib import md5

from .models import File
from .. import db

SAVE_PATH = os.path.dirname(os.path.abspath(__file__))+'/../static/img'

def savepic(file_):
    '''
    save pic data and return file object
    '''
    fm = file_.filename.rsplit('.', 1)[1]
    filename = md5(os.urandom(64)).hexdigest()+'.'+fm
    file_.save('%s/%s' % (SAVE_PATH, filename))
    f = File(filename=filename)    
    db.session.add(f)
    # db.session.commit()
    return f

def changepic(product_obj, file_):
    '''
    change product object 's pic
    '''
    filename = product_obj.pic.filename
    try:
        os.remove('%s/%s' % (SAVE_PATH, filename))
    except:
        pass
    fm = file_.filename.rsplit('.', 1)[1]
    filename = md5(os.urandom(64)).hexdigest()+'.'+fm
    file_.save('%s/%s' % (SAVE_PATH, filename))
    product_obj.pic.filename = filename
    db.session.add(product_obj)
    # db.session.commit()

def removepic(filename):
    '''
    remove file
    '''
    try:
        os.remove('%s/%s' % (SAVE_PATH, filename))
    except:
        pass
    File.query.filter_by(filename=filename).delete()
    # db.session.commit()

def copypic(product_obj):
    '''
    copy a pic for snapshot
    '''
    f = open('%s/%s' % (SAVE_PATH, product_obj.pic.filename), 'r')
    fm = product_obj.pic.filename.rsplit('.', 1)[1]
    filename = md5(os.urandom(64)).hexdigest()+'.'+fm
    nf = open('%s/%s' % (SAVE_PATH, filename), 'w')
    nf.write(f.read())
    f.close()
    nf.close()
    nf = File(filename=filename)
    db.session.add(nf)
    # db.session.commit()
    return nf

