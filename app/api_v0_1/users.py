from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import User, ReadPermission
from ..email import send_email

@api.route('/user/<int:id>')
def get_user(id):
    if not ReadPermission.has_permission(id, g.current_user.id):
        return forbidden('permission denied')
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/user/change_email', methods=['POST'])
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
def change_password():
    new_password = request.json.get('new_password')
    if new_password is None or new_password == '':
        raise ValidationError('mission new password argument')
    g.current_user.password = new_password
    db.session.add(g.current_user)
    return jsonify({'message': 'Your password has been updated.'}, 202)

