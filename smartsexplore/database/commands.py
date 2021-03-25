"""
Flask management commands to perform on the SMARTSexplore database.
"""

import click

from flask import Blueprint
from flask.cli import with_appcontext


def attach_to_blueprint(blueprint: Blueprint):
    """
    Attaches all available commands to the given :class:`flask.Blueprint` object.

    :param blueprint: The blueprint object to attach the commands to.
    """
    blueprint.cli.command('init')(init_db_command)


@with_appcontext
def init_db_command():
    """
    Initialize the db with table definitions and base data.
    """
    from smartsexplore.database.util import init_db
    init_db()
    click.echo("Initialized the database.")
