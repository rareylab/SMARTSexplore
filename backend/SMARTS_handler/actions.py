"""
Functions that interact with the database and external programs to manage SMARTS and SMARTS-SMARTS
match data.
"""
import logging

import click
from flask import current_app

import sys
sys.path.append('backend')

from database import SMARTS, get_session, get_smarts, UndirectedEdge, \
    DirectedEdge, NoSMARTSException

sys.path.append('bin/commands')
from parsers import parse_smartscompare


def add_library(name: str, filename: str) -> None:
    """
    Add a SMARTS library (name and a .smarts file) to the db, by adding corresponding SMARTS
    objects to the database.

    Note that, if available, the SMARTS label will be used as the newly created SMARTS objects'
    names. This is typically a tab- or space-separated string that comes after each SMARTS pattern
    in the .smarts file.

    :param name: The name of the library to add. Will be stored on the created SMARTS instances.
    :param filename: The filename of the .smarts file to create and store SMARTS from.
    """
    import re
    session = get_session()

    with open(filename, 'r', encoding="utf-8") as stream:  # TODO maybe some line documentation
        ignored_lines = []
        nof_added_smarts = 0
        for i, line in enumerate(stream):
            line = line.strip()
            if line.startswith('#'):
                continue
            m = re.search(r'(^[^\s]+)\s+(.+)$', line)
            if m:
                smarts_pattern = m.group(1)
                smarts_name = m.group(2)
                smarts = SMARTS(name=smarts_name, pattern=smarts_pattern, library=name)
                session.add(smarts)
                nof_added_smarts += 1
            else:
                ignored_lines.append(i+1)  # take care of 0 indexing!

    session.commit()
    click.echo(f"Added {nof_added_smarts} SMARTS to the database as library {name}.")
    if ignored_lines:
        click.echo("Ignored lines: " + ", ".join(map(str, ignored_lines)))


def calculate_edges(mode):
    """
    Calculate and add edges between all SMARTS in the database.

    Currently implements modes 'Similarity' and
    'SubsetOfFirst'. 'SubsetOfSecond' is redundant, and 'Identical' is
    currently just not implemented.

    When 'Similarity' mode is chosen, 0.1 is picked as a fixed
    similarity value lower bound; otherwise a too large number of
    edges for our purposes would (generally) be generated.
    """
    import tempfile
    import os
    import sys
    sys.path.append('bin/commands')
    from util import run_process

    # Check validity of chosen mode
    implemented_modes = ('Similarity', 'SubsetOfFirst')
    if mode not in implemented_modes:
        raise ValueError(f"{mode} is not an implemented mode. Implemented modes are: "
                         f"{', '.join(implemented_modes)}")

    # Get a DB session, retrieve all SMARTS patterns, and write them into file
    session = get_session()

    print("SMARTS")
    try:
        smartsfile = get_smarts()
    except NoSMARTSException:
        logging.warning("No SMARTS in the database! Exiting the edge calculation process...")

    # Get mode ID
    mode_map = {'Identical': 1, 'SubsetOfFirst': 2, 'SubsetOfSecond': 3, 'Similarity': 4}
    mode_id = mode_map[mode]

    # Run SMARTScompare on the temporary SMARTS file, and write the
    # stdout to a new temporary result output file.
    smartscomparefile = tempfile.NamedTemporaryFile(mode='r+', encoding="utf-8")

    compare_cmd = [
        current_app.config['SMARTSCOMPARE_PATH'],
        "D:\\BachelorAMD\\MYSMARTSexplore\\test_smarts.smarts",
        # smartsfile.name,
        '-M', '-1',
        # discard edges with <= 0.1 similarity when using (undirected) mode "Similarity"
        *(['-t', '0.1'] if mode == 'Similarity' else []),
        '-p', str(os.cpu_count() // 2),
        '-d', '|',
        '-D', '`',
        '-m', str(mode_id)
    ]
    # -d `
    print("PROCESS")
    run_process(compare_cmd, stdout=smartscomparefile, stderr=sys.stderr)
    smartscomparefile.seek(0)  # must rewind before further usage

    # Parse the SMARTScompare output
    print("ITERATOR")
    parse_iterator = parse_smartscompare(smartscomparefile)
    resultfile_mode = next(parse_iterator)
    assert resultfile_mode == mode,\
        f"Mode of the SMARTScompare output, {resultfile_mode}, does not match specified mode, {mode}!"

    # --- Code to store results in the database starts here ---

    # Get the existing edges in the database and store them in memory, for efficient checks
    print("EDGES")
    existing_edges = _get_existing_edges(mode, session)
    nof_added_edges = 0
    duplicate_edges = []
    print("DUPLICATES")
    # Define a function to check for duplicates

    def _check_for_duplicates(left, right):
        if (left, right) in existing_edges:
            duplicate_edges.append((left, right))
            return True
        else:
            return False

    # Different loops and logic based on mode
    print("MODE")
    if mode == 'Similarity':
        for (line_no, lname, rname, mcssim, spsim) in parse_iterator:
            lsmarts = session.query(SMARTS).filter_by(id=int(lname)).first()
            rsmarts = session.query(SMARTS).filter_by(id=int(rname)).first()
            losmarts, hismarts = (lsmarts, rsmarts) if lsmarts.id < rsmarts.id\
                else (rsmarts, lsmarts)
            assert losmarts.id != hismarts.id, f'   {lname} {lsmarts}\n== {rname} {rsmarts}'
            assert losmarts.id < hismarts.id

            if not _check_for_duplicates(losmarts.id, hismarts.id):
                edge = UndirectedEdge(low_smarts=losmarts, high_smarts=hismarts,
                                      mcssim=mcssim, spsim=spsim)
                print("edge: ", edge)
                existing_edges.add((losmarts.id, hismarts.id))
                session.add(edge)
                nof_added_edges += 1
    elif mode == 'SubsetOfFirst':
        for (line_no, lname, rname, mcssim, spsim) in parse_iterator:
            lsmarts = session.query(SMARTS).filter_by(id=int(lname)).first()
            rsmarts = session.query(SMARTS).filter_by(id=int(rname)).first()
            fromsmarts, tosmarts = rsmarts, lsmarts

            if not _check_for_duplicates(fromsmarts.id, tosmarts.id):
                edge = DirectedEdge(from_smarts=fromsmarts, to_smarts=tosmarts,
                                    mcssim=mcssim, spsim=spsim)
                existing_edges.add((fromsmarts.id, tosmarts.id))
                session.add(edge)
                nof_added_edges += 1

    # Commit the session and close all temporary files
    session.commit()
    print("end")
    smartsfile.close()
    smartscomparefile.close()


def _get_existing_edges(mode, session):
    """
    Gets a set object of existing edges from the DB, corresponding to the SMARTScompare mode.
    The set will contain 2-tuples representing each edge.
    """
    if mode == 'Similarity':
        return set(
            (e.low_id, e.high_id) for e in session.query(UndirectedEdge).all()
        )
    elif mode == 'SubsetOfFirst':
        return set(
            (e.from_id, e.to_id) for e in session.query(DirectedEdge).all()
        )
    else:
        raise ValueError(f"Unimplemented mode: {mode}")
