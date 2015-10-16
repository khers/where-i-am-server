from datetime import datetime
from flask import render_template, flash, redirect, session, url_for
from flask.ext.login import login_required, current_user
from . import main
from .. import db
from ..models import User
from .forms import DisplayForm

@main.route('/')
def start():
    return redirect(url_for('auth.login'))

@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = DisplayForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        # Was the data a valid nickname?
        if user is None:
            # Nope, was it an email?
            user = User.query.filter_by(email=form.string.data).first()
            if user is None:
                flash('Invalid username or password.')
                return redirect(url_for('main.index'))
        return redirect(url_for('main.display', nickname=user.nickname)
    return render_template('index.html', form=form)

@main.route('/display/<nickname>')
@login_required
def display(nickname):
    target_user = User.query.filter_by(nickname=nickname).first()
    if target_user is None:
        flash('Invalid username or password.')
        return redirect(url_for('main.index'))
        results = sorted(target_user.locations, key=lambda loc:loc.when, reverse=True)
        target = { 'nickname': target_user.nickname
#    target = { 'nickname': 'name',
#               'locations': [
#                 {
#                   'date_str': 
#                   'latitude':
#                   'longitude':
#                 },
#                 ...
#               ]
#             }
    return render_template('display.html', user=current_user, target=target)

