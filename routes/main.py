from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('dashboard.dashboard_view'))

@main_bp.route('/about')
def about_view():
    return render_template('about.html')
