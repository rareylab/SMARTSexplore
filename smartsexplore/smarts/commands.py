"""
Flask management commands for this modular app. Try ``flask smarts``.

Exposes commands for:

    * inserting SMARTS into the database
      (:func:`add_library_command`, :func:`add_libraries_command`),
    * calculating SMARTS-SMARTS relationships
      (:func:`calculate_edges`),
    * drawing SMARTS and SMARTS-SMARTS in the SMARTSViewer visual language
      (:func:`draw_all_smarts_command`, :func:`draw_all_subsets_command`)
"""
import os

import click
from flask import current_app, Blueprint
from flask.cli import with_appcontext
from sqlalchemy.orm import subqueryload

from smartsexplore.database import get_session, SMARTS, DirectedEdge
from smartsexplore.smarts.draw import draw_multiple_smarts, draw_multiple_smarts_subset_relations
from smartsexplore.smarts.actions import add_library, calculate_edges


def attach_to_blueprint(blueprint: Blueprint):
    """
    Attaches all available commands to the given :class:`flask.Blueprint` object.

    :param blueprint: The blueprint object to attach the commands to.
    """
    blueprint.cli.command('draw_all_smarts')(draw_all_smarts_command)
    blueprint.cli.command('draw_all_subsets')(draw_all_subsets_command)
    blueprint.cli.command('add_library')(add_library_command)
    blueprint.cli.command('add_libraries')(add_libraries_command)
    blueprint.cli.command('calculate_edges')(calculate_edges_command)


@with_appcontext
def draw_all_smarts_command():
    """
    Draws all SMARTS in the db to the serving directory.

    This is a required action before serving the application in
    production, for the frontend to work correctly.
    """
    session = get_session()
    all_smarts = session.query(SMARTS).all()
    viewer_path = current_app.config['SMARTSCOMPARE_VIEWER_PATH']
    output_path = current_app.config['STATIC_SMARTSVIEW_PATH']
    os.makedirs(output_path, exist_ok=True)
    if not os.path.isfile(viewer_path):
        raise ValueError(f"Viewer path {viewer_path} does not point to a file...!")

    return draw_multiple_smarts(all_smarts, viewer_path, output_path)


@with_appcontext
def draw_all_subsets_command():
    """
    Draws all DirectedEdges in the db to the serving directory.

    This is a required action before serving the application in
    production, for the frontend to work correctly.
    """
    session = get_session()
    all_edges = session.query(DirectedEdge).options(
        subqueryload(DirectedEdge.from_smarts),
        subqueryload(DirectedEdge.to_smarts)
    ).all()
    viewer_path = os.path.join(current_app.root_path,
                               current_app.config['SMARTSCOMPARE_VIEWER_PATH'])
    output_path = current_app.config['STATIC_SMARTSVIEW_SUBSETS_PATH']
    os.makedirs(output_path, exist_ok=True)
    if not os.path.isfile(viewer_path):
        raise ValueError(f"Viewer path {viewer_path} does not point to a file...!")

    return draw_multiple_smarts_subset_relations(all_edges, viewer_path, output_path)


@click.argument('name')
@click.argument('filename')
@with_appcontext
def add_library_command(name, filename):
    """
    Add a SMARTS library (name & .smarts file) to the db.
    """
    session = get_session()
    if session.query(SMARTS).filter_by(library=name).count() > 0:
        answer = input(
            f"There are already SMARTS with this library name ({name}) in the database.\n"
            f"Are you sure you want to add them? Enter Y to continue [y/N] ")
        if answer.lower() != 'y':
            click.echo(f"{name} was *not* inserted.")
            return None

    return add_library(name, filename)


@click.argument('file_names', nargs=-1)
@with_appcontext
def add_libraries_command(file_names):
    """
    Add multiple SMARTS libraries at once, taking the library names from the filenames
    """
    base_names = [os.path.basename(file_name) for file_name in file_names]
    lib_names = [base_name.rpartition('.smarts')[0] for base_name in base_names]

    # Ask the user for verification of our interpretation
    print("I will insert the following libraries (filename --> library name):")
    for file_name, lib_name in zip(file_names, lib_names):
        print(f'{file_name} --> {lib_name}')
    answer = input("Is that okay? Enter Y to continue [y/N] ")
    if answer.lower() != 'y':
        click.echo("Aborted! Database was not modified.")
        return

    # Run the import via multiple add_library calls
    for file_name, lib_name in zip(file_names, lib_names):
        add_library(name=lib_name, filename=file_name)

    print(f"Imported {len(lib_names)} libraries ({', '.join(lib_names)}).")


@click.argument('mode')
@with_appcontext
def calculate_edges_command(mode):
    """
    Calculates edges between all SMARTS in the database, and stores those in the database.
    Available modes are (SubsetOfFirst, Similarity). SubsetOfFirst will construct directed
    edges describing a subset relation, Similarity will construct undirected edges describing only
    a similarity relation.
    """
    return calculate_edges(mode)
