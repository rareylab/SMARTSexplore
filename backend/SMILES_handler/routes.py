"""
Routes for uploading and retrieving molecules and SMARTS-molecule match data stored in the database,
plus structure diagram images of these molecules.
"""
import logging
import os

import werkzeug
from flask import Blueprint, request, current_app, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename

from ..database import get_session, Molecule, MoleculeSet, Match
from .actions import calculate_molecule_matches
from .draw import draw_molecules_from_molset


def attach_to_blueprint(blueprint: Blueprint):
    """
    Attaches all available routes to the given :class:`flask.Blueprint` object.

    :param blueprint: The blueprint object to attach the commands to.
    """
    blueprint.route('/upload', methods=['POST'])(upload_molecule_set)
    blueprint.route('/matches/<int:id>', methods=['GET'])(matches_for_molecule_set)
    blueprint.route('/images/<int:id>', methods=['GET'])(deliver_molecule_image)


def _check_valid_file(file: werkzeug.datastructures.FileStorage):
    """
    Verifies that a given file is a valid molecule file with respect to the restrictions
    defined in the current app config (ALLOWED_MOLECULE_SET_EXTENSIONS and
    MAX_UPLOADED_MOLECULE_NUMBER).

    Ignores lines starting with # when counting the number of molecules.

    .. warning:: Does not verify that the file adheres to the SMILES format!
    """
    allowed_extensions = current_app.config['ALLOWED_MOLECULE_SET_EXTENSIONS']
    user_filename = file.filename
    if not ('.' in user_filename and user_filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        raise ValueError("Please upload a .smi or .smiles file!")

    try:
        lines = [line.decode('utf-8') for line in file.readlines()]
    except UnicodeError:
        raise ValueError(
            'Could not decode file as UTF8 text! Are you sure this is a molecule file?'
        )

    nof_molecule_lines = len([line for line in lines if not line.startswith('#')])
    max_molecules = current_app.config['MAX_UPLOADED_MOLECULE_NUMBER']
    if nof_molecule_lines > max_molecules:
        raise ValueError(
            f"You seem to have uploaded {nof_molecule_lines} molecules. "
            f"Please upload a file with {max_molecules} molecules or less!"
        )
    file.seek(0)
    return file


def upload_molecule_set():
    """
    A route for uploading a set of molecules, given as a single SMILES file in the 'file' parameter.

    On success, redirects to the route :func:`matches_for_molecule_set` for the newly created
    MoleculeSet. Therefore, on success this returns the matches associated with the
    uploaded molecule set.

    On failure, responds with a 400 error and JSON containing a descriptive error string
    (key 'error'). This string can be displayed directly in the frontend.
    """
    if 'file' not in request.files or not request.files['file'].filename:
        return {'error': 'Request seems to be missing a molecule file.'}, 400

    plain_file = request.files['file']

    try:
        file = _check_valid_file(plain_file)
    except ValueError as e:
        return {'error': str(e)}, 400

    mol_set = None
    try:
        mol_set = calculate_molecule_matches(file)
        draw_molecules_from_molset(mol_set)
        # delete the temporary files
        if os.path.exists(current_app.config['TMP_SMARTS_PATH']):
            os.remove(current_app.config['TMP_SMARTS_PATH'])
        if os.path.exists(current_app.config['TMP_SMILES_PATH']):
            os.remove(current_app.config['TMP_SMILES_PATH'])
        return matches_for_molecule_set(id=mol_set.id)  # redirect(url_for('molecules.matches_for_molecule_set', id=mol_set.id))
    except Exception as e:
        logging.error(e)
        if mol_set is not None:
            session = get_session()
            session.delete(mol_set)
            session.commit()
        return {'error': 'Unknown error occurred'}, 500


def matches_for_molecule_set(id: int):
    """
    A route that retrieves all matches associated with a MoleculeSet instance.
    Responds with a JSON object containing the ``molecule_set_id``, as well as an array of
    ``matches``. Each match in ``matches`` will have a ``molecule_id``, a ``molecule_name``
    and a ``smarts_id``.

    :param id: The ID of the MoleculeSet instance.
    :return: JSON as described above.
    """
    session = get_session()
    molset = session.query(MoleculeSet).get(id)
    if molset is None:
        return {'error': 'Unknown molecule set.'}, 404

    molecule_ids = session.query(Molecule.id).filter_by(molset_id=molset.id)
    matches = session.query(Match).filter(Match.molecule_id.in_(molecule_ids))
    return {
        'matches': [
            {
                'molecule_set_id': molset.id,
                'molecule_id': match.molecule_id,
                'molecule_name': match.molecule.name,
                'smarts_id': match.smarts_id
            }
            for match in matches
        ]
    }, 200


def deliver_molecule_image(id):
    """
    A route that delivers the image for a molecule, given the molecule's ID.
    Responds with 404 if the molecule or its image could not be found.

    :param id: The ID of the molecule.
    :return: A file response on success, a 404 response on error.
    """
    session = get_session()
    molecule = session.query(Molecule).get(id)
    if molecule is None:
        return {'error': 'Molecule not found'}, 404

    subdir = secure_filename(str(molecule.molset_id))
    filename = secure_filename(f'{molecule.id}.svg')
    return send_from_directory(
        os.path.join(current_app.config['STATIC_MOL2SVG_MOLECULE_SETS_PATH'], subdir),
        filename
    )
