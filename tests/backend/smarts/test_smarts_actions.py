import pytest

from smartsexplore.database import SMARTS, DirectedEdge
from smartsexplore.smarts.actions import add_library, calculate_edges


@pytest.fixture
def example_smarts():
    smarts1 = SMARTS(name='TEST', pattern='PP', library='A')
    smarts2 = SMARTS(name='NO_phosphonate', pattern='P(=O)ON', library='A')
    smarts3 = SMARTS(name='TEST2', pattern='P', library='B')
    smarts4 = SMARTS(name='TEST3', pattern='C', library='C')
    return [smarts1, smarts2, smarts3, smarts4]


def test_calculate_edges_subset(session, example_smarts):
    """
    :Authors:
        Pia Plümer, Simon Welker
    """
    session.add_all(example_smarts)
    session.commit()

    calculate_edges('SubsetOfFirst')
    assert session.query(DirectedEdge).count() != 0
    assert session.query(DirectedEdge)\
        .filter(DirectedEdge.from_smarts.has(library='A')).count() == 2
    assert session.query(DirectedEdge)\
        .filter(DirectedEdge.from_smarts.has(library='B')).count() == 0
    assert session.query(DirectedEdge)\
        .filter(DirectedEdge.to_smarts.has(library='B')).count() == 2
    assert session.query(DirectedEdge)\
        .filter(  DirectedEdge.to_smarts.has(library='C')\
                | DirectedEdge.from_smarts.has(library='C')).count() == 0


def test_calculate_edges_raises_when_mode_is_invalid(session, example_smarts):
    """
    :Authors:
        Simon Welker
    """
    session.add_all(example_smarts)
    session.commit()

    for wrong_mode in ['', 'SubsetOfFirst!', 'Subsetoffirst', 'subsetoffirst',
                       'similarity', 'sim', ' ', '\n']:
        with pytest.raises(ValueError):
            calculate_edges(wrong_mode)


def test_data_from_file_smarts(session):
    filename = "./tests/backend/testdata/test_smarts.smarts"
    name = "bms"
    add_library(name, filename)
    # -----------------------------
    print(session.query(SMARTS).filter_by(pattern='this').all())
    assert session.query(SMARTS).count() == 180
