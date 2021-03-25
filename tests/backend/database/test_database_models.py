import pytest
from sqlalchemy.exc import IntegrityError

from smartsexplore.database import MoleculeSet, Molecule, SMARTS, Match


def test_model_creation(session):
    molset = MoleculeSet()
    molecule = Molecule(pattern='CCCC1CC1', name='', molset=molset)
    smarts = SMARTS(name='NO_phosphonate', pattern='P(=O)ON', library='BMS')
    match = Match(molecule=molecule, smarts=smarts)
    session.add(molecule)
    session.add(smarts)
    session.add(match)
    session.commit()

    assert session.query(Molecule).first().pattern == 'CCCC1CC1'
    assert session.query(Match).first().molecule.pattern == 'CCCC1CC1'
    assert session.query(Match).first().molecule.molset.id == molset.id


def test_validates_match_uniqueness(session):
    molset = MoleculeSet()
    molecule = Molecule(pattern='c1cccccc1', name='bonk', molset=molset)
    smarts = SMARTS(name='NO_phosphonate', pattern='P(=O)ON', library='bms')
    match1 = Match(molecule=molecule, smarts=smarts)
    match2 = Match(molecule=molecule, smarts=smarts)
    session.add(molecule)
    session.add(smarts)
    session.add(match1)
    session.add(match2)

    with pytest.raises(IntegrityError):
        session.commit()
