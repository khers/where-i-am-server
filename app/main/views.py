from datetime import datetime
from flask import render_template, flash, redirect, session, url_for
from flask.ext.login import login_required, current_user
from . import main
from .. import db
from ..models import User, Location, ReadPermission
from .forms import DisplayForm

@main.route('/')
def start():
    return redirect(url_for('auth.login'))

@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = DisplayForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.string.data).first()
        # Was the data a valid nickname?
        if user is None:
            # Nope, was it an email?
            user = User.query.filter_by(email=form.string.data).first()
            if user is None:
                flash('Invalid username or email.')
                return redirect(url_for('main.index'))
        return redirect(url_for('main.display', target=user.nickname))
    return render_template('index.html', form=form)

@main.route('/display/<target>')
@login_required
def display(target):
    target_user = User.query.filter_by(nickname=target).first()
    if target_user is None:
       flash('Invalid target name or email.')
       return redirect(url_for('main.index'))

    perms = ReadPermission.query.filter_by(grantor_id=target_user.id, grantee_id=current_user.id)
    if perms is None and current_user.id != target_user.id:
        flash("You don't have permission to read the target user's location data.")
        return redirect(url_for('main.index'))

    results = sorted(target_user.locations, key=lambda loc:loc.when, reverse=True)
    if not results:
        flash('The requested user does not have any available location data.')
        return redirect(url_for('main.index'))

    loc = results[0]
    target = { 'nickname': target_user.nickname,
               'locations': [
                   {
                       'date_str': loc.when,
                       'latitude': loc.latitude,
                       'longitude': loc.longitude
                    }
                   ]
               }
    return render_template('display.html', user=current_user, target=target)

