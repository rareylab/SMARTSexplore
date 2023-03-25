"""
Utility functions for easy access to the SMARTSexplore database and connected SQLAlchemy sessions.
"""
import tempfile
from typing import Dict

from flask import current_app, g, has_app_context
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import SMARTS, DirectedEdge, MoleculeSet, UndirectedEdge, Match, Molecule


def get_db(db_url=None):
    """
    Gets an SQLAlchemy session given a valid database URL.
    Must be called from within a Flask appcontext.
    :returns: A tuple of (engine object, sessionmaker instance).
    """
    if db_url is None:
        if has_app_context:
            db_url = current_app.config['DATABASE']
        else:
            raise ValueError("db_url cannot be None if working outside Flask app context!")

    engine = create_engine(db_url, connect_args={'check_same_thread': False})
    sm = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, sm


def get_session():
    """
    Gets an SQLAlchemy session to the app database, as defined by the DATABASE app config key.

    Must be called from within a Flask appcontext.

    If called within a Flask context where the `flask.g` object is available (e.g.,
    a running server), it gets the session from the `flask.g` object, or creates and stores it
    on the `flask.g` object. This session will be a scoped session (see SQLAlchemy ORM docs).

    If called within a context where the `flask.g` object is unavailable (e.g., management commands
    that are not tied to a running server, and only have the appcontext available), returns a
    non-scoped session and does not interact with `flask.g`.

    :returns: A (potentially scoped) SQLAlchemy session to the app database, see above.
    """
    if not g:
        engine, sm = get_db()
        session = sm()
        return session
    else:
        if 'session' not in g:
            engine, sm = get_db()
            session = scoped_session(sm)
            g.session = session
        return g.session


def close_session(e=None):
    """
    Closes the current SQLAlchemy session to the app database, if one was opened.
    """
    session = g.pop('session', None)
    if session is not None:
        session.remove()


def init_db() -> None:
    """
    Initializes the app database appropriately. Currently just means that the ORM model tables are
    created.
    Must be used within the Flask appcontext.
    """
    from .models import Base
    engine, sessionmaker = get_db()
    session = sessionmaker()
    Base.metadata.create_all(bind=engine)
    session.commit()


def reset_db() -> None:
    """
    Resets the app database. Currently just means that the ORM model tables get
    deleted.
    Must be used within the Flask appcontext.
    """
    session = get_session()
    session.query(Molecule).delete()
    session.query(MoleculeSet).delete()
    session.query(SMARTS).delete()
    session.query(Match).delete()
    session.query(UndirectedEdge).delete()
    session.query(DirectedEdge).delete()
    session.commit()


def reset_molecules() -> None:
    """
    Resets the molecules. Currently just means that the ORM model table gets deleted.
    Must be used within the Flask appcontext.
    """
    session = get_session()
    session.query(Molecule).delete()
    session.query(MoleculeSet).delete()
    session.query(Match).delete()
    session.commit()


def reset_edges() -> None:
    """
    Resets the edges. Currently just means that the ORM model table gets deleted.
    Must be used within the Flask appcontext.
    """
    session = get_session()
    session.query(DirectedEdge).delete()
    session.query(UndirectedEdge).delete()
    session.commit()


def get_molecules(molecules):
    """
    Writes a list of :class:`Molecule` objects to a temporary .smiles file, and returns a handle
    to that file.

    Will write each :class:`Molecule` as one line consisting of the molecule's SMILES pattern and
    its ID as the "label" of its output SMILES line, so that the resultant file can be passed to
    external tools and the output of those tools can be linked back to the corresponding
    :class:`Molecule` objects (as long as those external tools print the "label" of the processed
    molecule, of course).

    :returns: A tuple of:

      * The handle to the written temporary .smiles file
      * A dictionary mapping (line number) to (Molecule id)
    """
    import tempfile
    import os

    line_no_to_molecule_id = {}

    moleculefile = tempfile.NamedTemporaryFile(mode='r+', suffix='.smiles')
    text = '\n'.join(f'{mol.pattern}\t{mol.id}' for mol in molecules)
    moleculefile.write(text)

    for i, mol in enumerate(molecules):
        line_no = i+1
        line_no_to_molecule_id[line_no] = mol.id
    moleculefile.seek(0)

    if os.path.exists(current_app.config['TMP_SMILES_PATH']):
        os.remove(current_app.config['TMP_SMILES_PATH'])
    f = open(current_app.config['TMP_SMILES_PATH'], "x", encoding="utf-8")
    f.write(text)
    f.close()
    return moleculefile, line_no_to_molecule_id


class NoSMARTSException(Exception):
    """
    Raised by :func:`write_smarts_to_tempfile` if no SMARTS are available to write.
    """
    pass


def get_smarts() -> tempfile.NamedTemporaryFile:
    """
    Retrieves all SMARTS patterns currently stored in the database, and writes them out into a
    temporary file, using the IDs from the database as labels for each SMARTS object.
    
    :returns: A file handle to the written temporary .smarts file.
    :raises: :class:`NoSMARTSException`, if there are no SMARTS to be written.
    """
    import tempfile
    import os

    session = get_session()
    smartss = session.query(SMARTS).all()

    if len(smartss) == 0:
        raise NoSMARTSException("No SMARTS in the database to write to a file!")

    smartsfile = tempfile.NamedTemporaryFile(mode='r+', suffix='.smarts', encoding="utf-8")  # ,encoding="utf-8"
    text = '\n'.join(f'{smarts.pattern}\t{smarts.id}' for smarts in smartss)
    # smartsfile.write(b'{text}')
    smartsfile.write(text)
    smartsfile.seek(0)

    if os.path.exists(current_app.config['TMP_SMARTS_PATH']):
        os.remove(current_app.config['TMP_SMARTS_PATH'])
    f = open(current_app.config['TMP_SMARTS_PATH'], "x", encoding="utf-8")
    f.write(text)
    f.close()
    return smartsfile
