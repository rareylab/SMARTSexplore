import tempfile
from typing import Dict

from flask import current_app, g, has_app_context
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import SMARTS, DirectedEdge, MoleculeSet, UndirectedEdge, Match, Molecule


def get_db(db_url=None):
    if db_url is None:
        if has_app_context:
            db_url = current_app.config['DATABASE']
        else:
            raise ValueError("db_url cannot be None if working outside Flask app context!")

    engine = create_engine(db_url, connect_args={'check_same_thread': False})
    sm = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, sm


def get_session():
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
    session = g.pop('session', None)
    if session is not None:
        session.remove()


def init_db() -> None:
    from .models import Base
    engine, sessionmaker = get_db()
    session = sessionmaker()
    Base.metadata.create_all(bind=engine)
    session.commit()


def reset_db() -> None:
    session = get_session()
    session.query(Molecule).delete()
    session.query(MoleculeSet).delete()
    session.query(SMARTS).delete()
    session.query(Match).delete()
    session.query(UndirectedEdge).delete()
    session.query(DirectedEdge).delete()
    session.commit()


def reset_molecules() -> None:
    session = get_session()
    session.query(Molecule).delete()
    session.query(MoleculeSet).delete()
    session.query(Match).delete()
    session.commit()


def reset_edges() -> None:
    session = get_session()
    session.query(DirectedEdge).delete()
    session.query(UndirectedEdge).delete()
    session.commit()


def get_molecules(molecules):
    import tempfile
    import os

    line_no_to_molecule_id = {}

    moleculefile = tempfile.NamedTemporaryFile(mode='r+b', suffix='.smiles')  # ,dir="D:"
    text = '\n'.join(f'{mol.pattern}\t{mol.id}' for mol in molecules)
    moleculefile.write(b'{text}')

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
    pass


def get_smarts() -> tempfile.NamedTemporaryFile:
    import tempfile
    import os
    session = get_session()
    smartss = session.query(SMARTS).all()

    if len(smartss) == 0:
        raise NoSMARTSException("No SMARTS in the database to write to a file!")

    smartsfile = tempfile.NamedTemporaryFile(mode='r+b', suffix='.smarts', dir="D:")  # ,encoding="utf-8"
    text = '\n'.join(f'{smarts.pattern}\t{smarts.id}' for smarts in smartss)
    smartsfile.write(b'{text}')
    smartsfile.seek(0)

    if os.path.exists(current_app.config['TMP_SMARTS_PATH']):
        os.remove(current_app.config['TMP_SMARTS_PATH'])
    f = open(current_app.config['TMP_SMARTS_PATH'], "x", encoding="utf-8")
    f.write(text)
    f.close()
    return smartsfile
