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
    blueprint.cli.command('reset')(reset_db_command)
    blueprint.cli.command('reset_molecules')(reset_molecules_command)
    blueprint.cli.command('reset_edges')(reset_edges_command)


@with_appcontext
def init_db_command():
    """
    Initialize the db with table definitions and base data.
    """
    from .util import init_db
    init_db()
    click.echo("Initialized the database.")


@with_appcontext
def reset_db_command():
    """
    Reset the data in the db.
    """
    from .util import reset_db
    reset_db()
    click.echo("Reset the database.")


@with_appcontext
def reset_molecules_command():
    """
    Reset the molecules in the db.
    """
    from .util import reset_molecules
    reset_molecules()
    click.echo("Reset the molecules.")


def reset_edges_command():
    """
    Reset the edges in the db.
    """
    from .util import reset_edges
    reset_edges()
    click.echo("Reset the edges.")
