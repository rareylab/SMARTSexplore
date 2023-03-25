"""
Database definitions and management
Defines and interacts with an SQL database holding all relevant data for the SMARTSexplore
application. Uses SQLAlchemy for all of this definition and interaction.
Furthermore, uses SQLAlchemy's ORM feature to define all models in
:mod:`smartsexplore.database.models`.
"""

from flask import Blueprint

from .commands import attach_to_blueprint
from .models import *
from .util import *


bp = Blueprint('db', __name__)
bp.cli.short_help = 'Manage a SMARTSexplore database.'
attach_to_blueprint(bp)
