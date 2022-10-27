"""
Functions to retrieve JSON-renderable representations of graph data stored in the database.
"""
from backend.database import get_session, SMARTS, DirectedEdge


def from_db(min_similarity: float, max_similarity: float) -> dict:
    """Generates a dict representation of all directed graph data stored in the database, consisting
    of all stored SMARTS nodes (key 'nodes') and those stored directed edges (key 'edges') whose
    spsim property fulfils (interval min_similarity <= spsim <= max_similarity).

    :param min_similarity: The minimum similarity of the returned edges (inclusive).
    :param max_similarity: The maximum similarity of the returned edges (exclusive).
    :return: A dict of the available graph data as described.
    """
    session = get_session()
    smarts = session.query(SMARTS).all()
    edges = session.query(DirectedEdge).filter(
        DirectedEdge.spsim >= min_similarity,
        DirectedEdge.spsim <= max_similarity
    ).all()
    num_of_sets = 1
    graph_dict = {
        'nodes': [
            {
                'id': i*len(smarts) + smart.id,
                'name': smart.name,
                'library': smart.library,
                'pattern': smart.pattern
            }
            for smart in smarts
            for i in range(num_of_sets)
        ]
        ,
        'edges': [
            {
                'id': i*len(edges)+edge.id,
                'source': i*len(smarts)+edge.from_id,
                'target': i*len(smarts)+edge.to_id,
                'mcssim': edge.mcssim,
                'spsim': edge.spsim
            }
            for edge in edges
            for i in range(num_of_sets)
        ]
    }
    return {'dic': graph_dict}
