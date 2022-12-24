"""
:Authors:
    Pia Plümer
"""

import os
import tempfile

from flask import current_app
from sqlalchemy.orm import subqueryload

from backend.database import SMARTS, DirectedEdge
from backend.SMARTS_handler.draw import draw_one_smarts, draw_one_smarts_subset_relation, \
    draw_multiple_smarts, draw_multiple_smarts_subset_relations


def test_draw_one_smarts(session):
    smarts = SMARTS(name='2halo_pyrazine_3EWG', pattern='[#7;R1]1[#6]([F,Cl,Br,I])[#6]([$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C=O)])[#7][#6][#6]1', library='A')
    session.add(smarts)
    session.commit()

    fake_viewer_path = current_app.config['SMARTSCOMPARE_VIEWER_PATH']
    with tempfile.TemporaryDirectory() as fake_output_path:
        current_app.config['STATIC_SMARTSVIEW_PATH'] = fake_output_path
        draw_one_smarts(session.query(SMARTS).first(),fake_viewer_path, fake_output_path)
        assert os.path.isdir(fake_output_path)
        assert os.path.isfile(os.path.join(fake_output_path, f'{smarts.id}.svg'))


def test_draw_multiple_smarts(session):
    smarts = [
        SMARTS(name='2halo_pyrazine_3EWG', pattern='[#7;R1]1[#6]([F,Cl,Br,I])[#6]([$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C=O)])[#7][#6][#6]1', library='A'),
        SMARTS(name='monofluoroacetate', pattern='[C;H2](F)C(=O)[O,N,S]', library='A'),
        SMARTS(name='sulfite_sulfate_ester', pattern='[C,c]OS(=O)O[C,c]', library='B')
    ]

    session.add_all(smarts)
    session.commit()

    viewer_path = current_app.config['SMARTSCOMPARE_VIEWER_PATH']
    with tempfile.TemporaryDirectory() as fake_output_path:
        current_app.config['STATIC_SMARTSVIEW_PATH'] = fake_output_path
        draw_multiple_smarts(session.query(SMARTS).all(), viewer_path, fake_output_path)
        assert os.path.isdir(fake_output_path)
        print(os.listdir(fake_output_path))
        files = [
            x for x in os.listdir(fake_output_path)
            if os.path.isfile(os.path.join(fake_output_path, x))
            and x.endswith('.svg')
        ]
        assert len(files) == len(smarts)


def test_draw_one_smarts_subset_relation(session):
    smarts1 = SMARTS(name='Chloramidine', pattern='[Cl]C([C&R0])=N', library='SureChEMBL')
    smarts2 = SMARTS(name='halo_imino', pattern='C(=[#7])([Cl,Br,I,$(O(S(=O)(=O)))])', library='BMS')
    session.add(smarts1)
    session.add(smarts2)
    dir_edge = DirectedEdge(from_smarts=smarts1, to_smarts=smarts2, mcssim= 0.7, spsim=0.7)
    session.add(dir_edge)
    session.commit()

    viewer_path = current_app.config['SMARTSCOMPARE_VIEWER_PATH']
    with tempfile.TemporaryDirectory() as fake_output_path:
        current_app.config['STATIC_SMARTSVIEW_SUBSETS_PATH'] = fake_output_path
        draw_one_smarts_subset_relation(session.query(DirectedEdge).first(), viewer_path, fake_output_path)
        expected_output_path = fake_output_path
        assert os.path.isdir(expected_output_path)
        assert os.path.isfile(os.path.join(expected_output_path, f'{dir_edge.id}.svg'))


def test_draw_multiple_smarts_subset_relations(session):
    smarts = [
        SMARTS(name='2halo_pyrazine_3EWG', pattern='[#7;R1]1[#6]([F,Cl,Br,I])[#6]([$(S(=O)(=O)),$(C(F)(F)(F)),$(C#N),$(N(=O)(=O)),$([N+](=O)[O-]),$(C=O)])[#7][#6][#6]1', library='A'),
        SMARTS(name='monofluoroacetate', pattern='[C;H2](F)C(=O)[O,N,S]', library='A'),
        SMARTS(name='sulfite_sulfate_ester', pattern='[C,c]OS(=O)O[C,c]', library='B'),
        SMARTS(name='test', pattern='CCCCc1ccccc1', library='B')
    ]
    edges = [
        DirectedEdge(from_smarts=smarts[0], to_smarts=smarts[1], mcssim=0.7, spsim=0.7),
        DirectedEdge(from_smarts=smarts[1], to_smarts=smarts[2], mcssim=0.7, spsim=0.7),
        DirectedEdge(from_smarts=smarts[2], to_smarts=smarts[0], mcssim=0.7, spsim=0.7)
    ]

    session.add_all(smarts)
    session.add_all(edges)
    session.commit()

    viewer_path = current_app.config['SMARTSCOMPARE_VIEWER_PATH']
    with tempfile.TemporaryDirectory() as fake_output_path:
        current_app.config['STATIC_SMARTSVIEW_SUBSETS_PATH'] = fake_output_path
        all_edges = session.query(DirectedEdge).options(
            subqueryload(DirectedEdge.from_smarts),
            subqueryload(DirectedEdge.to_smarts)
        ).all()

        draw_multiple_smarts_subset_relations(all_edges, viewer_path, fake_output_path)
        assert os.path.isdir(fake_output_path)
        files = [
            x for x in os.listdir(fake_output_path)
            if os.path.isfile(os.path.join(fake_output_path, x))
            and x.endswith('.svg')
        ]
        assert len(files) == len(edges)
