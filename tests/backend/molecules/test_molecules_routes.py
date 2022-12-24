"""
:Authors:
    Simon Welker
"""

import io
import random

import pytest
import werkzeug

from sqlalchemy.sql.expression import func

from backend.database import MoleculeSet, Molecule, SMARTS, Match
from backend.SMILES_handler.draw import draw_molecules_from_molset

MOLECULE_UPLOAD_URL = '/molecules/upload'
GET_MATCHES_URL = '/molecules/matches/'
GET_IMAGES_URL = '/molecules/images/'


@pytest.fixture
def smarts_molecules_and_matches(session):
    smartss = [
        SMARTS(name=f'xyz{i}', pattern='C', library='test')
        for i in range(3)
    ]
    molsets = [MoleculeSet(), MoleculeSet()]
    molecules = []
    matches = []

    for j in range(10):
        molecule = Molecule(name=f'mol{j}', pattern='CCC', molset=molsets[j % 2])
        molecules.append(molecule)
        for smarts in random.sample(smartss, 2):
            match = Match(molecule=molecule, smarts=smarts)
            matches.append(match)

    session.add_all(smartss)
    session.add_all(molsets)
    session.add_all(molecules)
    session.add_all(matches)
    session.commit()

    return {
        'molsets': molsets,
        'smartss': smartss,
        'molecules': molecules,
        'matches': matches
    }


def test_matches_for_existing_molsets_have_valid_format(client, session, smarts_molecules_and_matches):
    molsets = smarts_molecules_and_matches['molsets']

    for i in range(len(molsets)):
        response = client.get(GET_MATCHES_URL + str(molsets[i].id))
        assert response.status_code == 200

        json = response.json
        assert 'molecule_set_id' in json
        assert json['molecule_set_id'] == molsets[i].id
        assert 'matches' in json
        assert isinstance(json['matches'], list)
        expected_nof_matches = session.query(Match)\
            .filter(Match.molecule.has(molset=molsets[i])).count()
        assert len(json['matches']) == expected_nof_matches

        for match in json['matches']:
            assert 'molecule_id' in match
            assert 'molecule_name' in match
            assert 'smarts_id' in match

            assert session.query(Match).filter(
                (Match.molecule_id == match['molecule_id'])
                & (Match.smarts_id == match['smarts_id'])
            ).count() > 0

            assert session.query(Molecule).get(match['molecule_id']).name == match['molecule_name']


def test_matches_for_inexistent_molsets_return_404(client, session, smarts_molecules_and_matches):
    highest_molset_id = session.query(func.max(MoleculeSet.id)).first()[0]
    for i in range(1, 10):
        nonexistent_id = highest_molset_id + i
        response = client.get(GET_MATCHES_URL + str(nonexistent_id))
        assert response.status_code == 404


def test_get_existing_molecule_image(client, smarts_molecules_and_matches):
    molsets = smarts_molecules_and_matches['molsets']
    molecules = smarts_molecules_and_matches['molecules']
    for molset in molsets:
        draw_molecules_from_molset(molset)

    # all molecules created in the smarts_molecules_and_matches fixture should lead to 200 response
    # and also their content type should be SVG
    for molecule in molecules:
        response = client.get(GET_IMAGES_URL + str(molecule.id))
        assert response.status_code == 200
        assert 'image/svg+xml' in response.content_type


def test_get_inexistent_molecule_image(client, session, smarts_molecules_and_matches):
    molsets = smarts_molecules_and_matches['molsets']
    for molset in molsets:
        draw_molecules_from_molset(molset)

    # inexistent IDs should lead to 404
    highest_molecule_id = session.query(func.max(Molecule.id)).first()[0]
    for i in range(1, 10):
        nonexistent_id = highest_molecule_id + i
        response = client.get(GET_IMAGES_URL + str(nonexistent_id))
        assert response.status_code == 404


def test_molecule_upload_should_fail_without_file(client):
    response = client.post(MOLECULE_UPLOAD_URL)
    assert response.status_code == 400
    assert 'missing' in response.json['error']
    assert 'file' in response.json['error']


def _mk_file(bin_contents, filename, content_type='chemical/x-daylight-smiles'):
    return werkzeug.datastructures.FileStorage(
        stream=io.BytesIO(bin_contents),
        filename=filename,
        content_type=content_type
    )


def _upload_molecule(client, file=None):
    data = {'file': file} if file is not None else None
    return client.post(MOLECULE_UPLOAD_URL,
                       data=data,
                       follow_redirects=True,
                       content_type='multipart/form-data')


def test_molecule_upload_should_fail_for_wrong_extensions(client, smarts_molecules_and_matches):
    wrong_ext_file = _mk_file(b'CCC triplecarbon', filename='actually_a_smiles.jpg')
    response = _upload_molecule(client, wrong_ext_file)
    assert response.status_code == 400
    assert 'upload' in response.json['error']


def test_molecule_upload_should_fail_for_binary_file(client, smarts_molecules_and_matches):
    binary_file = _mk_file(
        b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00>\x00\x01\x00\x00\x00\x00\xfa@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\xf0\x17\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x008',
        filename='not_really_a_smiles.smiles',
    )
    response = _upload_molecule(client, binary_file)
    assert response.status_code == 400
    assert 'decod' in response.json['error']


def test_molecule_upload_should_succeed_when_adhering_to_limits(client, app, smarts_molecules_and_matches):
    ok_smiles_file = _mk_file(
        b'CCC triplecarbon\n' * app.config['MAX_UPLOADED_MOLECULE_NUMBER'],
        filename='allowed.smi'
    )
    response = _upload_molecule(client, ok_smiles_file)
    assert response.status_code == 200


def test_molecule_upload_should_fail_for_too_many_molecules(client, app, smarts_molecules_and_matches):
    too_large_smiles_file = _mk_file(
        b'CCC triplecarbon\n' * (app.config['MAX_UPLOADED_MOLECULE_NUMBER'] + 1),
        filename='toolarge.smi'
    )
    response = _upload_molecule(client, too_large_smiles_file)
    assert response.status_code == 400


def test_molecule_upload_should_fail_for_wrong_smiles(client, smarts_molecules_and_matches):
    smiles_file = _mk_file(b'ABXYZ affe\n', filename='elwrongo.smi')
    response = _upload_molecule(client, smiles_file)
    # 500 for now, but with better checks might be 400 in the future
    assert response.status_code in [400, 500]


def test_successful_molecule_upload_should_affect_database(client, session, smarts_molecules_and_matches):
    nof_molecule_sets_pre = session.query(MoleculeSet).count()
    nof_molecules_pre = session.query(Molecule).count()
    nof_smarts_pre = session.query(SMARTS).count()
    nof_matches_pre = session.query(Match).count()

    ok_smiles_file = _mk_file(b'C singlecarbon\n', filename='ok.smi')
    response = _upload_molecule(client, ok_smiles_file)
    assert response.status_code == 200

    assert session.query(MoleculeSet).count() == nof_molecule_sets_pre + 1
    assert session.query(Molecule).count() == nof_molecules_pre + 1
    assert session.query(SMARTS).count() == nof_smarts_pre
    assert session.query(Match).count() > nof_matches_pre


def test_successful_molecule_upload_should_return_matches(client, session, smarts_molecules_and_matches):
    ok_smiles_file = _mk_file(b'C singlecarbon\n', filename='ok.smi')
    response = _upload_molecule(client, ok_smiles_file)
    assert response.status_code == 200

    json = response.json
    assert 'molecule_set_id' in json
    new_mol_set = session.query(MoleculeSet).get(json['molecule_set_id'])
    assert len(new_mol_set.molecules) == 1
    new_mol = new_mol_set.molecules[0]

    for match in json['matches']:
        assert match['molecule_id'] == new_mol.id
        assert match['molecule_name'] == 'singlecarbon'
