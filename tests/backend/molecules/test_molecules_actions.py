import pytest

from smartsexplore.database import MoleculeSet, Molecule, SMARTS, Match
from smartsexplore.molecules.actions import calculate_molecule_matches, \
    create_molecules_from_smiles_file


def test_nodematches(session):
    """
    :Authors:
        Pia Plümer
    """
    smarts1 = SMARTS(name='2halo_pyrazine_3EWG', pattern='[#7;R1]1[#6]([F,Cl,Br,I])[#6]([$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C=O)])[#7][#6][#6]1', library='A')
    smarts2 = SMARTS(name='NO_phosphonate', pattern='P(=O)ON', library='A')
    smarts3 = SMARTS(name='halogen_heteroatom', pattern='[!C;!c;!H][F,Cl,Br,I]', library='B')
    session.add(smarts1)
    session.add(smarts2)
    session.add(smarts3)
    session.commit()
    molset_count = session.query(MoleculeSet).count()

    with open("./tests/backend/testdata/test_molecules.smi", "rb") as file:
        calculate_molecule_matches(file)

    assert session.query(Match).count() != 0
    assert session.query(MoleculeSet).count() == molset_count + 1


def test_data_from_file(session):
    """
    :Authors:
        Pia Plümer
    """
    database_len = 0
    file_name = "./tests/backend/testdata/test_molecules.smi"
    test_file = open(file_name, "r")
    data = test_file.readlines()
    molset = MoleculeSet()
    for i in data:
        molecule = Molecule(pattern=i.split()[0], molset=molset, name="test_molecules")
        session.add(molecule)
    session.commit()
    # -----------------------------
    found = False
    for row in session.query(Molecule):
        database_len += 1
        if row.pattern == 'Clc1c(OC)ccc(c1)CNc2nnc(N3CCC(O)CC3)c4c2cc(C#N)cc4':
            found = True
    assert found
    assert database_len == len(data)
    test_file.close()


def test_search_in_database(session):
    """
    :Authors:
        Pia Plümer
    """
    file_name1 = open("./tests/backend/testdata/test_molecules_split1.smi", "rb+")
    file_name2 = open("./tests/backend/testdata/test_molecules_split2.smi", "rb+")

    mol_id1 = create_molecules_from_smiles_file(file_name1)
    mol_id2 = create_molecules_from_smiles_file(file_name2)
    # -----------------------------
    assert mol_id1.id != mol_id2.id
    found = False
    for row in session.query(Molecule).all():
        if row.pattern == 'Clc1c(OC)ccc(c1)CNc2nnc(N3CCC(O)CC3)c4c2cc(C#N)cc4':
            found = True
    assert found


def test_molmatches_succeeds_even_when_no_smarts_are_available(session):
    """
    :Authors:
        Simon Welker
    """
    assert session.query(SMARTS).count() == 0
    assert session.query(Molecule).count() == 0

    with open("./tests/backend/testdata/test_molecules.smi", "rb") as file:
        calculate_molecule_matches(file)

    assert session.query(SMARTS).count() == 0
    assert session.query(Match).count() == 0
    assert session.query(Molecule).count() != 0


def test_molmatches_deletes_molset_if_error_occurs(session, app):
    """
    :Authors:
        Simon Welker
    """
    session.add(SMARTS(name='NO_phosphonate', pattern='P(=O)ON', library='A'))
    session.commit()

    app.config['MATCHTOOL_PATH'] = 'xyz'

    nof_molsets = session.query(MoleculeSet).count()
    nof_mols = session.query(Molecule).count()
    with open("./tests/backend/testdata/test_molecules.smi", "rb") as file:
        with pytest.raises(Exception):
            calculate_molecule_matches(file)
    assert session.query(MoleculeSet).count() == nof_molsets
    assert session.query(Molecule).count() == nof_mols
