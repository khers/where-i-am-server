from app import db
from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import User, ReadPermission

@api.route('/permissions/add_read', methods=['POST'])
def add_read():
    target = request.json.get('target')
    if target is None:
        raise ValidationError('missing target argument')

    perm = ReadPermission.query.filter_by(grantor_id=g.current_user.id, grantee_id=target).first()
    if perm is None:
        perm = ReadPermission()
        perm.grantor_id = g.current_user.id
        perm.grantee_id = target
        db.session.add(perm)
    return jsonify({'result': 201})

@api.route('/permissions/del_read', methods=['POST'])
def del_read():
    target = request.json.get('target')
    if target is None:
        raise ValidationError('missing target argument')

    perm = ReadPermission.query.filter_by(grantor_id=g.current_user.id, grantee_id=target).first()
    if perm is not None:
        db.session.delete(perm)
    return jsonify({'result': 200})
