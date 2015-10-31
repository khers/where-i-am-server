from datetime import datetime, timezone
from flask import render_template, flash, redirect, session, url_for, request
from flask.ext.login import login_required, current_user
from . import main
from .. import db
from ..models import User, Location, ReadPermission
from .forms import DisplayForm, LocationForm

@main.route('/')
def start():
    return redirect(url_for('auth.login'))

@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = DisplayForm()
    options = [(current_user.id, current_user.nickname)]
    for perm in ReadPermission.query.filter_by(grantee_id=current_user.id):
        user = User.query.get(perm.grantor_id)
        if user is None:
            continue
        options.append((user.id, user.nickname))
    form.target.choices = options

    if form.validate_on_submit():
        user = User.query.filter_by(id=form.target.data).first()
        # Was the data a valid nickname?
        if user is None:
            flash('Invalid username or email.')
            return redirect(url_for('main.index'))
        return redirect(url_for('main.display', target=user.id, count=form.count.data))
    return render_template('index.html', form=form)

@main.route('/display/<int:target>/<int:count>')
@login_required
def display(target, count):
    target_user = User.query.filter_by(id=target).first()
    if target_user is None:
       flash('Invalid target user.')
       return redirect(url_for('main.index'))

    if not ReadPermission.has_permission(target, current_user.id):
        flash("You don't have permission to read the target user's location data.")
        return redirect(url_for('main.index'))

    results = Location.load_count(target, count)
    if not results:
        flash('The requested user does not have any available location data.')
        return redirect(url_for('main.index'))
    locations = []
    for loc in results:
        locations.append({'date_str': loc.when, 'latitude': loc.latitude, 'longitude': loc.longitude})
    data = { 'nickname': target_user.nickname,
               'locations': locations
               }
    return render_template('display.html', user=current_user, target=data)

@main.route('/add_location', methods=['GET', 'POST'])
@login_required
def add_location():
    form = LocationForm()
    if request.method == 'GET':
        form.when.data = datetime.now(timezone.utc)
    if form.validate_on_submit():
        loc = Location()
        loc.latitude = form.latitude.data
        loc.longitude = form.longitude.data
        loc.when = form.when.data
        loc.user_id = current_user.id
        db.session.add(loc)
        flash('Location entry added.')
        return redirect(url_for('main.index'))
    return render_template('add_location.html', form=form)

