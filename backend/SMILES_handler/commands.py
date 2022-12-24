import click
from flask import current_app, Blueprint
from flask.cli import with_appcontext
from sqlalchemy.orm import subqueryload

from ..database import get_session, Molecule, MoleculeSet
from .draw import draw_molecules_from_molset
from .actions import add_moleculeset


def attach_to_blueprint(blueprint: Blueprint):
    """
    Attaches all available commands to the given :class:`flask.Blueprint` object.

    :param blueprint: The blueprint object to attach the commands to.
    """
    blueprint.cli.command('add_moleculeset')(add_moleculeset_command)
    blueprint.cli.command('add_moleculesets')(add_moleculesets_command)


@click.argument('name')
@click.argument('filename')
@with_appcontext
def add_moleculeset_command(name, filename):
    session = get_session()
    if session.query(MoleculeSet).filter_by(molset=name).count() > 0:
        answer = input(
            f"There are already SMILES with this Molset name ({name}) in the database.\n"
            f"Are you sure you want to add them? Enter Y to continue [y/N] ")
        if answer.lower() != 'y':
            click.echo(f"{name} was *not* inserted.")
            return

    return add_moleculeset(name, filename)


@click.argument('file_names', nargs=-1)
@with_appcontext
def add_moleculesets_command(file_names):
    import os

    base_names = [os.path.basename(file_name) for file_name in file_names]
    lib_names = [base_name.rpartition('.smi')[0] for base_name in base_names]

    # Ask the user for verification of our interpretation
    print("I will insert the following libraries (filename --> MolSet name):")
    for file_name, lib_name in zip(file_names, lib_names):
        print(f'{file_name} --> {lib_name}')
    answer = input("Is that okay? Enter Y to continue [y/N] ")
    if answer.lower() != 'y':
        click.echo("Aborted! Database was not modified.")
        return

    # Run the import via multiple add_library calls
    for file_name, lib_name in zip(file_names, lib_names):
        add_moleculeset(name=lib_name, filename=file_name)

    print(f"Imported {len(lib_names)} Molsets ({', '.join(lib_names)}).")
