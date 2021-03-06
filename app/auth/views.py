from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, ReadPermission, Location
from ..mailer import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, DeleteLocationsForm
from .forms import PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, PermissionsForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    nickname=form.nickname.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your Where I Am account', 'auth/email/confirm',
                   user=user, token=token)
        flash('A confirmation email has been sent to your address.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('auth.unconfirmed'))
    return redirect(url_for('main.index'))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your Where I Am account', 'auth/email/confirm',
               user=current_user, token=token)
    flash('A new confirmation email has been sent to your address.')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('mail.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                    'auth/email/reset_password',
                    user=user, token=token,
                    next=request.args.get('next'))
        flash('An email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

@auth.route('/delete_locations', methods=['GET', 'POST'])
@login_required
def delete_locations():
    options = [(-1, 'All'),]
    for loc in Location.query.filter_by(user_id=current_user.id):
        options.append((loc.id, loc.when))
    form = DeleteLocationsForm(request.form)
    form.locations.choices = options
    if request.method == 'POST' and form.validate():
        if not form.confirm.data:
            flash('Not deleting location(s) becuase you were not sure.')
        else:
            loc_ids = set(form.locations.data)
            if -1 in loc_ids:
                Location.delete_all_by_user(current_user)
            else:
                Location.delete_set(loc_ids, current_user)
            flash('Deleted selected locations.')
        return redirect(url_for('main.index'))

    return render_template('auth/delete_locations.html', form=form)

@auth.route('/change_permissions', methods=['GET', 'POST'])
@login_required
def change_permissions():
    users = dict()

    user_ids = set()
    for user in User.query.all():
        if user.id == current_user.id:
            continue
        user_ids.add(user.id)
        users[user.id] = user
    reader_ids = set()
    for perms in ReadPermission.query.filter_by(grantor_id=current_user.id):
        reader_ids.add(perms.grantee_id)

    all_opts = []
    for user_id in user_ids:
        all_opts.append((user_id,users[user_id].nickname))
    user_ids -= reader_ids
    available_opts = []
    for user_id in user_ids:
        available_opts.append((user_id,users[user_id].nickname))
    can_read_opts = []
    for user_id in reader_ids:
        can_read_opts.append((user_id,users[user_id].nickname))

    form = PermissionsForm(request.form)
    if request.method == 'POST':
        form.can_read.choices = all_opts
        form.available.choices = all_opts
        if form.validate():
            new_reader_ids = set(form.can_read.data)
            for user_id in form.can_read.data:
                if user_id in reader_ids:
                    continue
                perm = ReadPermission()
                perm.grantor_id = current_user.id
                perm.grantee_id = user_id
                db.session.add(perm)
            # Any entry that was there before the form and is not there now
            # needs to be removed
            for user_id in reader_ids - new_reader_ids:
                perm = ReadPermission.query.filter_by(grantor_id=current_user.id, grantee_id=user_id).first()
                db.session.delete(perm)
            flash('Permissions updated.')
            return redirect(url_for('main.index'))

    form.available.choices = available_opts
    form.can_read.choices = can_read_opts

    return render_template('auth/change_permissions.html', form=form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and \
       not current_user.confirmed and \
       request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))

