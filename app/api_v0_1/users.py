from flask import jsonify, request, current_app, url_for, g
from . import api
from .decorators import authentication_required
from ..models import User, ReadPermission
from ..mailer import send_email

@api.route('/user/<int:id>')
@authentication_required()
def get_user(id):
    if not ReadPermission.has_permission(id, g.current_user.id):
        return forbidden('permission denied')
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/user/<nickname>')
@authentication_required()
def lookup_user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        return not_found('requested user not found')
    if not ReadPermission.has_permission(user.id, g.current_user.id):
        return forbidden('permission denied')
    return jsonify(user.to_json())

@api.route('/user/change_email', methods=['POST'])
@authentication_required()
def change_email():
    new_email = request.json.get('new_email')
    if new_email is None or new_email == '':
        raise ValidationError('missing new email address argument')
    token = g.current_user.generate_email_change_token(new_email)
    send_email(new_email, 'Confirm your email address',
               'auth/email/change_email',
               user=g.current_user, token=token)
    return jsonify({'message':
        'An email with instructions to confirm your new email address has been sent to you.'}, 202)

@api.route('/user/change_password', methods=['POST'])
@authentication_required()
def change_password():
    new_password = request.json.get('new_password')
    if new_password is None or new_password == '':
        raise ValidationError('mission new password argument')
    g.current_user.password = new_password
    db.session.add(g.current_user)
    return jsonify({'message': 'Your password has been updated.'}, 202)

