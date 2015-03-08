# -*- coding: utf-8 -*-
# from flask import request
# from flask.ext.login import login_required

# from . import picbp
# from .. import db

# from .models import File, Promotion
# from .utils import savepic, removepic
# from ..admin.utils import root_required

# @picbp.route('/promotion/create', methods=['POST', ])
# @login_required
# @root_required
# def create_promotion():
#     f = request.files.file
#     file_obj = savepic(f)
#     p = Promotion(pic=f)
#     db.session.add(p)
#     db.session.commit(p)
#     return jsonResponse({'id': p.id})

# @picbp.route('/promotion/delete/<filename>')
# @login_required
# @root_required
# def delete_promotion(filename):
#     removepic(filename)
    
