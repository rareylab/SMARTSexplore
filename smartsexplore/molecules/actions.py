"""
Functions that interact with the database and external programs to manage molecule and
molecule-SMARTS match data.
"""
import logging
import tempfile
import sys

from typing import BinaryIO

from flask import current_app

from smartsexplore.database import get_session, MoleculeSet, Molecule, SMARTS, Match, \
    write_smarts_to_tempfile, molecules_to_temporary_smiles_file, NoSMARTSException
from smartsexplore.parsers import parse_moleculematch
from smartsexplore.util import run_process


def create_molecules_from_smiles_file(file: BinaryIO) -> MoleculeSet:
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
        else:
            pattern = line_contents[0]
            name = ''
        pattern, name = pattern.strip(), name.strip()

        molecule = Molecule(pattern=pattern, name=name, molset=molset)
        session.add(molecule)
        nof_mol += 1
    session.commit()
    logging.info("Added %s Molecules to the database.", nof_mol)
    return molset


def calculate_molecule_matches(uploaded_molecules_file: BinaryIO) -> MoleculeSet:
    """
    Calculate molecule matches of all SMARTS in the database given a molecule file,
    and store the Molecule and Match instances in the database.

    :param uploaded_molecules_file: An open file handle to a molecule file to match
    """
    moleculefile, smartsfile, moleculematchfile = [None] * 3

    # get all SMARTS patterns in file
    mol_set = None
    try:
        session = get_session()
        mol_set = create_molecules_from_smiles_file(uploaded_molecules_file)
        moleculefile, _ = molecules_to_temporary_smiles_file(mol_set.molecules)
        try:
            smartsfile = write_smarts_to_tempfile()
        except NoSMARTSException:
            session.commit()
            return mol_set

        # Run moleculematch on the temporary SMARTS file, and write the
        # stdout to a new temporary result output file.
        moleculematchfile = tempfile.NamedTemporaryFile(mode='w+')
        match_cmd = [
            current_app.config['MATCHTOOL_PATH'],
            '-i', '2',
            '-m', moleculefile.name,
            '-s', smartsfile.name
        ]
        run_process(match_cmd, stdout=moleculematchfile, stderr=sys.stderr, reraise_exceptions=True)
        moleculematchfile.seek(0)

        # Parse the moleculematch output
        parse_iterator = parse_moleculematch(moleculematchfile)

        # --- Code to store results in the database starts here ---
        for (smartsid, moleculeid) in parse_iterator:
            mmol = session.query(Molecule).get(moleculeid)
            msmarts = session.query(SMARTS).get(smartsid)
            newmatch = Match(molecule=mmol, smarts=msmarts)
            session.add(newmatch)

        # Commit the session
        session.commit()
        return mol_set
    except Exception as exception:
        if mol_set is not None:  # clean up molset if exception occurred
            session = get_session()
            session.delete(mol_set)
            session.commit()
        raise exception
    finally:  # close all open file handles
        if uploaded_molecules_file:
            uploaded_molecules_file.close()
        if moleculefile:
            moleculefile.close()
        if smartsfile:
            smartsfile.close()
        if moleculematchfile:
            moleculematchfile.close()
