"""
:Authors:
    Simon Welker
"""

import json
import random

import pytest
from sqlalchemy import func
from sqlalchemy.orm import subqueryload

from smartsexplore.database import SMARTS, DirectedEdge
from smartsexplore.smarts.draw import draw_multiple_smarts, draw_multiple_smarts_subset_relations

DATA_URL = '/smarts/data'
IMAGE_URL = '/smarts/smartsview/'
SUBSET_IMAGE_URL = '/smarts/smartssubsets/'

NSMARTS = 72
NEDGES = 21


@pytest.fixture
def smarts_with_edges(session):
    smartss = []
    edges = []

    for i in range(NSMARTS):
        smarts = SMARTS(name=f'xyz{i}', pattern='ccc', library='test')
        smartss.append(smarts)
        session.add(smarts)

    from_to = random.sample(smartss, NEDGES * 2)
    for k in range(len(from_to) // 2):
        from_, to_ = from_to[2*k:2*k+2]
        if from_ == to_:
            continue
        edge = DirectedEdge(from_smarts=from_, to_smarts=to_,
                            mcssim=random.random(), spsim=random.random())
        edges.append(edge)
        session.add(edge)

    session.commit()
    return {'smarts': smartss, 'edges': edges}


@pytest.fixture
def drawn_smarts_with_edges(session, app, smarts_with_edges):
    smarts = session.query(SMARTS)\
        .filter(SMARTS.id.in_([s.id for s in smarts_with_edges['smarts']]))\
        .all()
    edges = session.query(DirectedEdge) \
        .options(subqueryload(DirectedEdge.from_smarts), subqueryload(DirectedEdge.to_smarts))\
        .filter(DirectedEdge.id.in_([s.id for s in smarts_with_edges['edges']]))\
        .all()

    draw_multiple_smarts(
        smarts,
        viewer_path=app.config['SMARTSCOMPARE_VIEWER_PATH'],
        output_path=app.config['STATIC_SMARTSVIEW_PATH']
    )
    draw_multiple_smarts_subset_relations(
        edges,
        viewer_path=app.config['SMARTSCOMPARE_VIEWER_PATH'],
        output_path=app.config['STATIC_SMARTSVIEW_SUBSETS_PATH']
    )

    import os
    print(os.listdir(app.instance_path))
    print(os.listdir(app.config['STATIC_SMARTSVIEW_PATH']))
    print(os.listdir(app.config['STATIC_SMARTSVIEW_SUBSETS_PATH']))

    return smarts_with_edges


def test_get_graph_data_via_post(client, session, smarts_with_edges):
    data = {'spsim_min': 0, 'spsim_max': 1}
    response = client.post(DATA_URL, data=json.dumps(data), content_type='application/json')
    graph_data = response.json
    assert 'nodes' in graph_data
    assert 'edges' in graph_data
    assert len(graph_data['nodes']) == NSMARTS
    assert len(graph_data['edges']) == NEDGES

    spsim_min, spsim_max = 0.3, 0.81
    nfiltered_edges = session.query(DirectedEdge).filter(
        DirectedEdge.spsim >= spsim_min, DirectedEdge.spsim <= spsim_max)\
        .count()
    data = {'spsim_min': spsim_min, 'spsim_max': spsim_max}
    response = client.post(DATA_URL, data=json.dumps(data), content_type='application/json')
    graph_data = response.json
    assert 'nodes' in graph_data
    assert 'edges' in graph_data
    assert len(graph_data['nodes']) == NSMARTS
    assert len(graph_data['edges']) == nfiltered_edges


def test_get_all_graph_data_via_get(client, smarts_with_edges):
    response = client.get(DATA_URL)
    graph_data = response.json
    assert 'nodes' in graph_data
    assert 'edges' in graph_data
    assert len(graph_data['nodes']) == NSMARTS
    assert len(graph_data['edges']) == NEDGES


def test_graph_data_invalid_request(client, smarts_with_edges):
    data = {'humbug': 420, 'haha': True}
    response = client.post(DATA_URL, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert 'nodes' not in response.json
    assert 'edges' not in response.json

    data = 'lol.exe'
    response = client.post(DATA_URL, data=data, content_type='application/octet-stream')
    assert response.status_code == 400
    assert 'nodes' not in response.json
    assert 'edges' not in response.json


def test_get_existing_smarts_image(client, drawn_smarts_with_edges):
    for smarts in drawn_smarts_with_edges['smarts']:
        response = client.get(IMAGE_URL + str(smarts.id))
        print(IMAGE_URL + str(smarts.id))
        print(response.status)
        assert response.status_code == 200
        assert 'image/svg+xml' in response.content_type


def test_get_inexistent_smarts_image(client, session, drawn_smarts_with_edges):
    highest_smarts_id = session.query(func.max(SMARTS.id)).first()[0]
    for i in range(1, 10):
        nonexistent_id = highest_smarts_id + i
        response = client.get(IMAGE_URL + str(nonexistent_id))
        assert response.status_code == 404


def test_get_existing_edge_image(client, drawn_smarts_with_edges):
    for edge in drawn_smarts_with_edges['edges']:
        response = client.get(SUBSET_IMAGE_URL + str(edge.id))
        assert response.status_code == 200
        assert 'image/svg+xml' in response.content_type


def test_get_inexistent_edge_image(client, session, drawn_smarts_with_edges):
    highest_smarts_id = session.query(func.max(SMARTS.id)).first()[0]
    for i in range(1, 10):
        nonexistent_id = highest_smarts_id + i
        response = client.get(IMAGE_URL + str(nonexistent_id))
        assert response.status_code == 404
