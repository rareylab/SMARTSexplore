from backend.database import Molecule, SMARTS, MoleculeSet, \
    get_smiles, get_smarts


def test_smarts_tempfile(session):
    smarts_patterns = [
        '[$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C(=O))]C#[C;!$(C-N);!$(C-n)]',
        '[N;!R]([$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C(=O))])=[N;!R]([$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C(=O))])',
        'O=COC=[$(C(S(=O)(=O))),$(C(C(F)(F)(F))),$(C(C#N)),$(C(N(=O)(=O))),$(C([N+](=O)[O-])),$(C(C(=O)));!$(C(N))]',
        'O(-S(=O)(=O))C=[$(C(S(=O)(=O))),$(C(C(F)(F)(F))),$(C(C#N)),$(C(N(=O)(=O))),$(C([N+](=O)[O-])),$(C(C(=O)));!$(C(N))]',
        '[C,c][C;!R](=O)[N;!R][C;!R](=O)[C,c]',
        '[#7;R1]1~[#7;R1]~[#7;R1](-C(=O))~[#6]~[#6]1',
        '[#7]1~[#7]~[#6]~[#7](-C(=O)[!N])~[#6]1',
        'O=C(-[!N])O[$([#7;+]),$(N(C=[O,S,N])(C=[O,S,N]))]'
    ]
    for i, pattern in enumerate(smarts_patterns):
        smarts = SMARTS(name=f'smarts{i}', pattern=pattern, library='test')
        session.add(smarts)
    session.commit()

    tmp_file = get_smarts()
    tmp_file.seek(0)
    lines = tmp_file.readlines()
    striplines = [line.strip() for line in lines]  # ignore whitespace, useful for last line tests

    assert len(lines) == len(smarts_patterns)

    for pattern in smarts_patterns:
        db_id = session.query(SMARTS).filter_by(pattern=pattern).first().id
        expected_line = f'{pattern}\t{db_id}'
        assert expected_line in striplines


def test_molecule_tempfile(session):
    molset = MoleculeSet()
    session.add(molset)
    smiles_patterns = [
        'O=C(Oc1ccccc1)N' + ('C' * i)
        for i in range(50)
    ]

    for i, pattern in enumerate(smiles_patterns):
        molecule = Molecule(pattern=pattern, name=f'mol{i}', molset=molset)
        session.add(molecule)
    session.commit()
    molfile, line_num = get_smiles(session.query(Molecule).all())
    molfile.seek(0)
    lines = molfile.readlines()
    striplines = [line.strip() for line in lines]  # ignore whitespace, useful for last line tests

    assert session.query(Molecule).count() == len(smiles_patterns)
    assert len(lines) == session.query(Molecule).count()

    for pattern in [
        'O=C(Oc1ccccc1)N',
        'O=C(Oc1ccccc1)NCCCCCCCC',
        'O=C(Oc1ccccc1)NCCCCCCCCCC',
        'O=C(Oc1ccccc1)N' + ('C' * 49)
    ]:
        db_id = session.query(Molecule).filter_by(pattern=pattern).first().id
        expected_line = f'{pattern}\t{db_id}'
        assert expected_line in striplines
