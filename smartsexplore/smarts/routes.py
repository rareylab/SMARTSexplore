"""
Routes for retrieving SMARTS and SMARTS-SMARTS relationship data stored in the database, as well as
image representations of these objects using the SMARTSViewer visual language [Schomburg2010]_.
"""

from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, send_from_directory, current_app

from . import to_json

def attach_to_blueprint(blueprint: Blueprint):
    """
    Attaches all available routes to the given :class:`flask.Blueprint` object.

    :param blueprint: The blueprint object to attach the commands to.
    """
    blueprint.route('/data', methods=['POST', 'GET'])(data)
    blueprint.route('/smartsview/<int:id>')(deliver_smartsview)
    blueprint.route('/smartssubsets/<int:id>')(deliver_smartssubset)


def data():
    """A route for getting the graph data, which includes all SMARTS stored in the database
    and all edges whose ``spsim`` property falls within the given range ``[spsim_min, spsim_max]``,
    given as POSTed JSON parameters.

    Returns 400 Bad Request if ``spsim_min`` or ``spsim_max`` are not given in the request.

    :return: Rendered JSON, as described above.
    :rtype: str
    """
    if request.method == 'GET':
        generated_graph = to_json.from_db(min_similarity=0, max_similarity=1)
        return generated_graph
    elif request.method == 'POST' and\
            request.is_json\
            and 'spsim_min' in request.json.keys()\
            and 'spsim_max' in request.json.keys():
        sim_min = float(request.json['spsim_min'])
        sim_max = float(request.json['spsim_max'])
        generated_graph = to_json.from_db(min_similarity=sim_min, max_similarity=sim_max)
        return generated_graph
    else:
        error_json = {'error': 'Invalid request.'}
        return jsonify(error_json), 400


def deliver_smartsview(id: int):
    """A route that delivers a static SMARTSview image, i.e., an SVG rendering of a single
    SMARTS object, given the integer ID of that SMARTS object.

    Does not verify existence of the SMARTS object itself, but will return a 404 response if
    the image for the SMARTS object does not exist.

    :param id: The ID of the SMARTS object to retrieve the SVG image of.
    :type id: int
    :return: A file response if the file exists, otherwise a 404 response.
    """
    filename = secure_filename(f'{id}.svg')
    return send_from_directory(
        current_app.config['STATIC_SMARTSVIEW_PATH'],
        filename
    )


def deliver_smartssubset(id: int):
    """A route that delivers a static SMARTScompareViewer image, i.e. an SVG rendering of the
    directed comparison of two SMARTS (DirectedEdge object), with matched nodes highlighted by
    connecting lines, given the integer ID of that DirectedEdge object.

    :param id: The ID of the DirectedEdge object to retrieve the SVG image of.
    :type id: int
    :return: A file response if the file exists, otherwise a 404 response.
    """
    filename = secure_filename(f'{id}.svg')
    return send_from_directory(
        current_app.config['STATIC_SMARTSVIEW_SUBSETS_PATH'],
        filename
    )
