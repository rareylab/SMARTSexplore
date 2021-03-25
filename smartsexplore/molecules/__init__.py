"""
A modular Flask app for generating, storing and serving molecule and molecule-SMARTS matching data,
along with corresponding images.

Depends on the :mod:`smartsexplore.database` module.
"""

from flask import Blueprint

from smartsexplore.molecules import routes

bp = Blueprint('molecules', __name__, url_prefix='/molecules')
bp.cli.short_help = 'Manage molecule and SMARTS-molecule match data.'
routes.attach_to_blueprint(bp)
