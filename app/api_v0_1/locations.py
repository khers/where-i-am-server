from flask import jsonify, request, current_app, url_for, g
from app import db
from . import api
from .decorators import authentication_required
from ..models import User, Location, ReadPermission
from datetime import datetime, timezone

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

@api.route('/locations/create', methods=['POST'])
@authentication_required()
def create_location():
    loc = Location.from_json(request.json, g.current_user.id)
    db.session.add(loc)
    resp = jsonify(loc.to_json())
    resp.status_code = 201
    return resp

