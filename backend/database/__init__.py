from flask import Blueprint

from .commands import attach_to_blueprint
from .models import *
from .util import *


bp = Blueprint('db', __name__)
bp.cli.short_help = 'Manage a SMARTSexplore database.'
attach_to_blueprint(bp)
