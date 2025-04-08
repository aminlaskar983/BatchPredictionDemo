"""
Main routes for the Gemini Batch Prediction web application.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard."""
    return render_template('dashboard.html')


@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')