from flask import jsonify, request, current_app, url_for, g
from app import db
from . import api
from .decorators import authentication_required
from ..models import User, Location, ReadPermission
from datetime import datetime

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
    start = datetime.fromtimestamp(request.json.get('start'), timezone.utc)
    if start is None:
        raise ValidationError('missing date start argument')
    end = datetime.fromtimestamp(request.json.get('end'), timezone.utc)
    if end is None:
        raise ValidationError('missing date end argument')

    locations = Location.load_date_range(target, start, end, count)
    return jsonify({ 'locations': [ loc.to_json() for loc in locations] })

@api.route('/locations/delete', methods=['POST'])
@authentication_required()
def delete_location():
    loc_ids = set(request.json.get('location_ids'))
    if -1 in loc_ids:
        if len(loc_ids) > 1:
            raise ValidationError('Cannot specify All (-1) and other locations together')
        Location.delete_all_by_user(g.current_user)
    else:
        Location.delete_set(loc_ids, g.current_user)
    return jsonify({'reponse': 'OK'})

@api.route('/locations/create', methods=['POST'])
@authentication_required()
def create_location():
    loc = Location.from_json(request.json, g.current_user.id)
    db.session.add(loc)
    resp = jsonify(loc.to_json())
    resp.status_code = 201
    return resp

