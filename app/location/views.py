# -*- coding: utf-8 -*-
from ..util.common import jsonResponse, jsonError
from .models import School, Building
from . import locationbp
from ..util.errno import LocationErrno

# ajax
@locationbp.route('/school_list', methods=['GET', ])
def get_school_list():
    return jsonResponse([{'id': i.id, 'name': i.name} for i in School.query.all()])

@locationbp.route('/<int:school_id>/building_list', methods=['GET', ])
def get_building_list(school_id):
    sc = School.query.filter_by(id=school_id).first()
    if not sc:
        return jsonError(LocationErrno.SCHOOL_DOES_NOT_EXIST)
    return jsonResponse([{'id': i.id, 'name': i.name} for i in sc.buildings.all()])
