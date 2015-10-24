from flask import jsonify, request, current_app, url_for, g
from . import api
from .decorators import authentication_required
from ..models import User, Location, ReadPermission

@api.route('/locations/last', methods=['POST'])
@authentication_required()
def get_last():
    count = int(request.json.get('count'))
    if count is None or count < 0:
        count = 1
    target = request.json.get('target')
    if target is None:
        raise ValidationError('missing target argument')

    if not ReadPermission.has_permission(target, g.current_user.id):
        return forbidden('permission denied')

    locations = Location.load_count(target, count)
    return jsonify({ 'locations': [ loc.to_json() for loc in locations] })

@api.route('/locations/range', methods=['POST'])
@authentication_required()
def get_range():
    target = request.json.get('target')
    if target is None:
        raise ValidationError('missing target argument')
    if not ReadPermission.has_permission(target, g.current_user.id):
        return forbidden('permission denied')

    count = int(request.json.get('count'))
    if count is None or count < 0:
        count = 0
    start = request.json.get('start')
    if start is None:
        raise ValidationError('missing date start argument')
    end = request.json.get('end')
    if end is None:
        raise ValidationError('missing date end argument')

    locations = Location.load_date_range(target, start, end, count)
    return jsonify({ 'locations': [ loc.to_json() for loc in locations] })

