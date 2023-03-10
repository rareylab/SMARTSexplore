"""
A modular Flask app for generating, storing and serving SMARTS and SMARTS-SMARTS edge data.
Depends on the :mod:`smartsexplore.database` module.
"""

from flask import Blueprint

from . import commands
from . import routes

bp = Blueprint('smarts', __name__, url_prefix='/smarts')
bp.cli.short_help = 'Manage SMARTS data.'
commands.attach_to_blueprint(bp)
routes.attach_to_blueprint(bp)
