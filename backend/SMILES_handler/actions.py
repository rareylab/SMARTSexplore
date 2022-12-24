"""
Functions that interact with the database and external programs to manage molecule and
molecule-SMARTS match data.
"""
import logging
from typing import BinaryIO

import os
import click
from flask import current_app

from ..database import get_session, MoleculeSet, Molecule, SMARTS, Match, \
    get_smarts, get_molecules, NoSMARTSException

from bin.commands.parsers import parse_moleculematch


def add_moleculeset(name: str, filename: str) -> None:
    import os
    session = get_session()

    with open(filename, 'r') as stream:  # TODO maybe some line documentation
        ignored_lines = []
        nof_added_smiles = 0
        molset = MoleculeSet()

        for i, line in enumerate(stream):
            line = line.strip()
            if line.startswith('#'):
                continue
            line_contents = line.split(None, 1)
            if len(line_contents) == 2:
                pattern, name = line_contents
                pattern, name = pattern.strip(), name.strip()
                molecule = Molecule(name=name, pattern=pattern, molset=molset)
                session.add(molecule)
                nof_added_smiles += 1
            else:
                ignored_lines.append(i+1)
    session.commit()
    click.echo(f"Added {nof_added_smiles} molecules to the database as library {name}.")
    if ignored_lines:
        click.echo("Ignored lines: " + ", ".join(map(str, ignored_lines)))


def add_moleculeset_from_file(file: BinaryIO) -> MoleculeSet:
    """
    Reads in a .smiles file and constructs :class:`Molecule` instances from it, all linked to a
    single new :class:`MoleculeSet` instance.

    :param file: A file handle to a .smiles file.
    :returns: The newly created :class:`MoleculeSet` instance. The created :class:`Molecule`
      instances are available as its ``.molecules`` property.
    """
    session = get_session()
    nof_mol = 0
    molset = MoleculeSet()

    for line in file:
        # Rudimentary SMILES parsing
        line = line.decode('utf-8')
        if line.startswith('#'):
            continue

        line_contents = line.split(None, 1)
        if len(line_contents) == 2:
            pattern, name = line_contents
        elif len(line_contents) == 1:
            pattern = line_contents[0]
            name = ''
        else:
            continue
        pattern, name = pattern.strip(), name.strip()
        molecule = Molecule(pattern=pattern, name=name, molset=molset)
        session.add(molecule)
        nof_mol += 1

    session.commit()
    logging.info(f"Added {nof_mol} Molecules to the database.")
    return molset


def calculate_molecule_matches(uploaded_molecules_file: BinaryIO) -> MoleculeSet:
    """
    Calculate molecule matches of all SMARTS in the database given a molecule file,
    and store the Molecule and Match instances in the database.

    :param uploaded_molecules_file: An open file handle to a molecule file to match
    """
    import tempfile
    import sys

    from bin.commands.util import run_process

    moleculefile, smartsfile, moleculematchfile = [None] * 3

    # get all SMARTS patterns in file
    mol_set = None
    try:
        session = get_session()
        mol_set = add_moleculeset_from_file(uploaded_molecules_file)
        moleculefile, _ = get_molecules(mol_set.molecules)
        try:
            smartsfile = get_smarts()
        except NoSMARTSException:
            session.commit()
            return mol_set

        # Run moleculematch on the temporary SMARTS file, and write the
        # stdout to a new temporary result output file.
        moleculematchfile = tempfile.NamedTemporaryFile(mode='w+t', encoding="utf-8")
        match_cmd = [
            current_app.config['MATCHTOOL_PATH'],
            '-i', '2',
            '-m', current_app.config['TMP_SMILES_PATH'],  # moleculefile.name,
            '-s', current_app.config['TMP_SMARTS_PATH']  # smartsfile.name
        ]
        run_process(match_cmd, stdout=moleculematchfile, stderr=sys.stderr, reraise_exceptions=True)
        moleculematchfile.seek(0)
        # Parse the moleculematch output
        parse_iterator = parse_moleculematch(moleculematchfile)
        # --- Code to store results in the database starts here ---
        for (smartsid, moleculeid) in parse_iterator:
            if(not smartsid or not moleculeid):
                continue
            mmol = session.query(Molecule).get(moleculeid)
            msmarts = session.query(SMARTS).get(smartsid)
            newmatch = Match(molecule=mmol, smarts=msmarts)
            session.add(newmatch)
        # Commit the session
        session.commit()
        return mol_set
    except Exception as e:
        if mol_set is not None:  # clean up molset if exception occurred
            session = get_session()
            session.delete(mol_set)
            session.commit()
        raise e
    finally:  # close all open file handles
        if os.path.exists(current_app.config['TMP_SMARTS_PATH']):
            os.remove(current_app.config['TMP_SMARTS_PATH'])
        if os.path.exists(current_app.config['TMP_SMILES_PATH']):
            os.remove(current_app.config['TMP_SMILES_PATH'])
        if uploaded_molecules_file:
            uploaded_molecules_file.close()
        if moleculefile:
            moleculefile.close()
        if smartsfile:
            smartsfile.close()
        if moleculematchfile:
            moleculematchfile.close()
