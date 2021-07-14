"""
Functions for drawing molecule structure diagrams. Uses the ``mol2svg`` NAOMI tool for this purpose.
"""
import os
import math
import shutil
import tempfile

from flask import current_app

from smartsexplore.database import MoleculeSet, molecules_to_temporary_smiles_file
from smartsexplore.util import run_process


def draw_molecules_from_molset(molset: MoleculeSet) -> None:
    """
    Draws all molecules contained in a set of molecules (a MoleculeSet instance) as SVG images,
    to the static molecule image path defined in the app config (STATIC_MOL2SVG_MOLECULE_SETS_PATH).

    A subfolder named by the MoleculeSet's ID will be created under the static path, and the
    molecule images will be stored inside that folder, named by their IDs ({id}.svg).

    :param molset: The MoleculeSet instance to render all molecules of.
    """

    molfile, line_no_to_molecule_id =\
        molecules_to_temporary_smiles_file(molset.molecules)
    # deal with mol2svg's output naming scheme being dependent on the number of input molecules...
    filename_nof_digits = int(math.ceil(math.log10(len(molset.molecules) + 1)))

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            draw_cmd = [
                current_app.config['MOL2SVG_PATH'],
                '-i', molfile.name,
                # mol2svg will infer img_1.svg, img_2.svg, ... from this
                '-o', os.path.join(tmpdirname, 'img.svg'),
                '-a',  # draw all in file, not just first
                '-P'  # use protonation as-is
            ]
            run_process(draw_cmd, reraise_exceptions=True)

            output_dir = os.path.join(
                current_app.config['STATIC_MOL2SVG_MOLECULE_SETS_PATH'],
                str(molset.id)
            )
            os.makedirs(output_dir, exist_ok=True)
            for line_no, molecule_id in line_no_to_molecule_id.items():
                # see def. of filename_of_digits above
                id_ = '{num:{fill}{width}}'.format(num=line_no, fill='0', width=filename_nof_digits)
                from_file = os.path.join(tmpdirname, f'img_{id_}.svg')
                to_file = os.path.join(output_dir, f'{molecule_id:d}.svg')
                if os.path.isfile(from_file):
                    shutil.move(from_file, to_file)
                else:
                    current_app.logger.warning(
                        f'Could not find expected mol2svg output file: {from_file}!'
                    )
    finally:
        molfile.close()
