/* eslint max-len: */
import * as Vue from 'vue';
import _ from 'lodash';

/**
 * Represents a node in a SMARTS graph. Stored properties are:
 *
 *   - id: a unique ID (preferably int or string)
 *   - name: A descriptive name of this node (string)
 *   - pattern: The SMARTS pattern of this node (string)
 *   - library: The name of the SMARTS library this node belongs to (string)
 *   - outgoingEdges: An array of outgoing edges (to be attached by an enclosing Graph)
 *   - incomingEdges: As above, but incoming edges.
 *   - incidentEdges: Combines outgoing and incoming edges.
 *   - meta: A dictionary to store arbitrary metadata about this node.
 */
class Node {
  /**
   * Constructs a new Node object from a 'plain node', i.e. an object that has
   * all properties documented for this class, apart from all the ...*Edges
   * properties and the .meta property.
   * @param {Object} plainNode A 'plain node' object as described above
   * @param {Object} defaultMeta (optional) an object containing keys with default
   *   values that will be assigned to the .meta property.
   */
  constructor(plainNode, defaultMeta = null) {
    this.id = plainNode.id;
    this.name = plainNode.name || '(unnamed SMARTS)';
    this.pattern = plainNode.pattern || '';
    this.library = plainNode.library || '(no library)';
    this.outgoingEdges = [];
    this.incomingEdges = [];
    this.incidentEdges = [];

    // Validation of input
    if (!this.pattern || (typeof this.pattern) !== 'string') {
      throw new Error(
          `Node must be given a nonempty pattern but was given '${this.pattern}'!`,
      );
    }

    this.meta = {};
    Object.assign(this.meta, _.cloneDeep(defaultMeta));
  }
};

/**
 * Represents an edge in a SMARTS graph. Stored properties are:
 *
 *   - id: a unique ID (preferably int or string)
 *   - mcssim: MCS similarity (float between 0.0 and 1.0)
 *   - spsim: SP similarity (float between 0.0 and 1.0)
 *   - type: a string describing the type this edge has (equal / subset)
 *   - source: the unique ID of the source Node object
 *   - target: the unique ID of the target Node object
 *   - meta: A dictionary to store arbitrary metadata about this edge.
 */
class Edge {
  /**
   * Constructs a new Edge object from a 'plain edge', i.e., an object that has
   * all properties documented for this class, apart from the .meta property.
   *
   * Can attach arbitrary metadata to the .meta property by passing default values
   * as an object `defaultMeta`.
   *
   * If the `getNodeFn` function parameter is passed, it will be called with the source
   * and target IDs to replace the .source and .target properties on the returned Edge,
   * by whatever values that function returns.
   * @param {Object} plainEdge A 'plain edge' object as described above
   * @param {Object} defaultMeta (optional) an object containing keys with default
   *   values that will be assigned to the .meta property.
   * @param {Function} getNodeFn (optional) A function that will be used to retrieve
   *   matching Node object for the source and target IDs.
   *   If not passed, .source and .target will be stored unchanged, i.e. as their IDs.
   */
  constructor(plainEdge, defaultMeta = null, getNodeFn = null) {
    getNodeFn = getNodeFn || _.identity;

    this.id = plainEdge.id;
    this.mcssim = plainEdge.mcssim;
    this.spsim = plainEdge.spsim;
    this.type = plainEdge.type || 'subset';
    this.source = getNodeFn(plainEdge.source);
    this.target = getNodeFn(plainEdge.target);

    // Validation of input
    if (!(this.type === 'equal' || this.type === 'subset')) {
      throw new Error(`Edge type must be 'equal' or 'subset', but '${this.type}' was given!`);
    }
    if (!(typeof this.mcssim === 'number') || this.mcssim < 0 || this.mcssim > 1) {
      throw new Error(
          `MCS similarity of edge must be a number between 0 and 1,
          but is '${this.mcssim}'!`);
    }
    if (!(typeof this.spsim === 'number') || this.spsim < 0 || this.spsim > 1) {
      throw new Error(
          `SP similarity of edge must be a number between 0 and 1,
          but is '${this.mcssim}'!`);
    }

    this.meta = {};
    Object.assign(this.meta, _.cloneDeep(defaultMeta));
  }
};

/**
 * A directed graph consisting of Node obejcts and Edge objects.
 */
class Graph {
  /**
   * Constructs a new Graph object from arrays 'nodes' and 'edges'. Allows the attachment of
   * metadata to every node and edge using a dictionary of default values for both.
   * @param {Array} nodes An array of plain-object nodes. See Node class for details.
   * @param {Array} edges An array of plain-object edges. See Edge class for details.
   * @param {Object} defaultNodeMeta (optional) an object containing default values for
   *   arbitrary keys, to be attached as metadata to every *node*.
   * @param {Object} defaultEdgeMeta (optional) an object containing default values for
   *   arbitrary keys, to be attached as metadata to every *edge*.
   * @param {Boolean} markEqualEdges (optional) If true (default), automatically detect equal
   *   edges, i.e., a pair of edges (l,r) and (r,l), and mark them as having .type == 'equal'.
   *   Will also remove one of each pair's edges, and sort the stored edges so that equal edges
   *   come last (useful for rendering order).
   */
  constructor(nodes, edges, defaultNodeMeta=null, defaultEdgeMeta=null, markEqualEdges=true) {
    // Store used 'plain' nodes and edges (used by plainClone)
    this._plainNodes = nodes;
    this._plainEdges = edges;
    // Store default meta definitions (used by _createNode, _createEdge)
    this._defaultNodeMeta = defaultNodeMeta;
    this._defaultEdgeMeta = defaultEdgeMeta;
    // Store lookup dicts for nodeid->node, edgeid->edge lookups
    this._idsToNodes = {};
    this._idsToEdges = {};

    // Copy and initialize nodes & edges
    this.nodes = _.map(nodes, (node) => this._createNode(node));
    this.edges = _.map(edges, (edge) => this._createEdge(edge));
    if (markEqualEdges) {
      this._findMarkAndSortEqualEdges();
    }
  }

  /**
   * Returns a clone of this graph simply by reusing the plain nodes, plain edges,
   * and their default meta values.
   *
   * Accordingly, will *not* copy any data updated after creation of this graph.
   * @return {Graph}
   */
  plainClone() {
    return new Graph(
        this._plainNodes, this._plainEdges,
        this._defaultNodeMeta, this._defaultEdgeMeta);
  }

  /**
   * Returns a Node by ID if present, undefined otherwise.
   * @param {any} id The ID of the Node to be returned.
   * @return {node}
   */
  getNodeById(id) {
    return this._idsToNodes[id];
  }

  /**
   * Returns an Edge by ID if present, undefined otherwise.
   * @param {any} id The ID of the Edge to be returned.
   * @return {edge}
   */
  getEdgeById(id) {
    return this._idsToEdges[id];
  }

  /**
   * Adds a new Node to this graph.
   * @param {Node} node The Node object to add. Must have a newly unique ID, or the
   *   behavior of this Graph is undefined.
   */
  addNode(node) {
    this.nodes.push(this._createNode(node));
  }

  /**
   * Adds a new Edge to this graph.
   * @param {Edge} edge The Edge object to add. Must have a newly unique ID, or the
   *   behavior of this Graph is undefined.
   */
  addEdge(edge) {
    this.edges.push(this._createEdge(edge));
  }

  /**
   * Runs a depth-first search through this graph starting from some Node,
   * calling arbitrary callback functions at each visited node and edge.
   * @param {Array} startNodes The Node object(s) to start the DFS from. Must be part of
   *   this Graph. Can pass a list of Nodes or a single Node.
   * @param {String} direction The direction(s) to traverse edges in.
   *   Can be 'outgoing', 'incoming', or 'all'.
   * @param {Number} maxDepth The maximum depth of the DFS. Convention: If maxDepth == 1,
   *   then exactly all directly adjacent nodes of `selectedNode` are visited.
   * @param {Function} visitedNodeCallback (optional) A callback that will be called for
   *   every visited node, with arguments: (visited node {Node}, current DFS depth {Number}).
   * @param {Function} visitedEdgeCallback (optional) A callback that will be called for
   *   every traversed edge, with arguments: (traversed edge {Edge}, edge outgoing? {Boolean})
   * @param {Function} beforeVisitCallback
   * @param {Function} edgeFilter
   *   filter edges to only active edges
   * @param {Function} nodeFilter
   *   filter nodes to only active nodes
   */
  runDFS(startNodes, direction, maxDepth,
      visitedNodeCallback=null, visitedEdgeCallback=null, beforeVisitCallback=null,
      edgeFilter=null, nodeFilter=null) {
    if (!(startNodes instanceof Array)) {
      startNodes = [startNodes];
    }
    _.each(startNodes, (startNode) => {
      if (!(startNode instanceof Node)) {
        throw new Error('At least one start node is not a Node object!');
      }
      if (!(startNode.id in this._idsToNodes)) {
        throw new Error('At least one start node ID was not found inside this Graph!');
      }
    });

    const lookup = {
      'outgoing': 'outgoingEdges',
      'incoming': 'incomingEdges',
      'all': 'incidentEdges',
    };
    const edgeProp = lookup[direction];

    const visited = {};
    /**
     * Help function for DFS
     * @param {*} node
     * @param {*} depth
     */
    function visitNode(node, depth) {
      if (nodeFilter && !nodeFilter(node)) return;

      if (visited[node.id] || depth > maxDepth) return;
      visited[node.id] = true;
      if (visitedNodeCallback) visitedNodeCallback(node, depth);

      _.each(node[edgeProp], function(edge) {
        if (edgeFilter && !edgeFilter(edge)) return;

        const isOutgoing = edge.source == node;
        const otherNode = isOutgoing ? edge.target : edge.source;
        if (
          ( isOutgoing && direction == 'outgoing') ||
          (!isOutgoing && direction == 'incoming') ||
          (direction == 'all')
        ) {
          if (visitedEdgeCallback) visitedEdgeCallback(edge, isOutgoing);
          visitNode(otherNode, depth+1);
        }
      });
    }

    _.each(startNodes, (startNode) => {
      if (nodeFilter && !nodeFilter(startNode)) return;
      if (beforeVisitCallback) beforeVisitCallback(startNode, visited[startNode.id]);
      visitNode(startNode, 0);
    });
  }

  /**
   * Calculates the connected components of this graph. Returns a 2-tuple of:
   *
   *   - a dict mapping (CC id) -> (list of nodes in CC)
   *   - a dict mapping (node id) -> (id of CC that contains this node)
   * @param {Function} edgeFilter (optional) a predicate to filter which edges will be traversed
   * @param {Function} nodeFilter (optional) a predicate to filter which nodes will be visited
   * @return {positions}
   */
  getCCs(edgeFilter=null, nodeFilter=null) {
    const nodes = this.nodes;
    let nofCC = 0;
    const nodeToCC = {};
    let ccs = {};
    this.runDFS(nodes, 'all', Infinity,
        (node) => { // node callback
          nodeToCC[node.id] = nofCC;
          ccs[nofCC].push(node);
        },
        null, // edge callback
        (node, previouslyVisited) => { // before node visit callback
          if (!previouslyVisited) {
            nofCC++;
            ccs[nofCC] = [];
            return true;
          }
          return false;
        },
        edgeFilter,
        nodeFilter,
    );
    ccs = _.map(ccs, (cc) => {
      return _.sortBy(cc, 'id');
    });

    return [ccs, nodeToCC];
  }

  /**
   * Sets node positions (x, y) to a grid, based on the connected components.
   *
   *   - Every node in one CC will be assigned the same position.
   *   - Nodes in CCs with at least 2 nodes are put into one--roughly quadratic--regular grid,
   *     ordered by corresponding CC size
   *   - Nodes in CCs with only one node (isolated nodes) are put into another
   *     --roughly quadratic--regular grid, separate from the first one.
   * @param {Function} edgeFilter (optional) a predicate to filter which edges will be traversed
   * @param {Function} nodeFilter (optional) a predicate to filter which nodes will be visited
   */
  setPositionsFromCCs(edgeFilter, nodeFilter) {
    // TODO: more flexibility in layout (especially offsets)
    let [ccs, nodeToCC] = this.getCCs(edgeFilter, nodeFilter);
    nodeToCC;
    ccs = _.sortBy(Object.values(ccs), (cc) => -cc.length); // TODO also consider identical edges?
    const [ccsMultiple, ccsSingle] = _.partition(ccs, (cc) => cc.length >= 2);

    // Multiple nodes per CC
    const perRow = Math.ceil(Math.sqrt(ccsMultiple.length));
    const offset = 500;
    const mid = (offset * (perRow - 1)) / 2;
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;

    _.each(ccsMultiple, function(cc, ccIdx) {
      const x = offset * (ccIdx % perRow) - mid;
      const y = offset * Math.floor(ccIdx / perRow) - mid;
      minX = Math.min(minX, x);
      maxX = Math.max(maxX, x);
      minY = Math.min(minY, y);
      maxY = Math.max(maxY, y);

      const perCCRow = Math.ceil(Math.sqrt(cc.length));
      _.each(cc, function(node, i) {
        node.x = x + 0.5 * (i % perCCRow);
        node.y = y + 0.5 * Math.floor(i / perCCRow);
      });
    });
    if (!ccsMultiple.length) { // handle case when there were no CCs with at least 2 nodes
      [minX, maxX, minY, maxX] = [0, 0, 0, 0];
    }

    // Single node per CC
    const baseX = maxX + offset;
    const baseY = minY;
    const perRowSingle = Math.ceil(Math.sqrt(ccsSingle.length));
    const offsetSingle = 100;
    _.each(ccsSingle, function(cc, ccIdx) {
      if (!cc.length) return;

      const x = baseX + offsetSingle * (ccIdx % perRowSingle);
      const y = baseY + offsetSingle * Math.floor(ccIdx / perRowSingle);
      cc[0].x = x;
      cc[0].y = y;
    });
  }

  /**
   * Creates and inserts a Node object from a plain-object description into this graph,
   * using the Node constructor.
   * @param {Object} plainNode The plain-object description of the node, e.g. received as JSON.
   * @return {node}
   */
  _createNode(plainNode) {
    const defaultMeta = this._defaultNodeMeta;
    const node = new Node(plainNode, defaultMeta);

    this._idsToNodes[node.id] = node;
    return node;
  }

  /**
   * Creates and inserts an Edge object from a plain-object description into this graph,
   * using the Edge constructor.
   * @param {*} plainEdge
   * @return {edge}
   */
  _createEdge(plainEdge) {
    if (!(plainEdge.source in this._idsToNodes)) {
      throw new Error(
          `Cannot create an edge with unknown source ID ${plainEdge.source}!`);
    }
    if (!(plainEdge.target in this._idsToNodes)) {
      throw new Error(
          `Cannot create an edge with unknown target ID ${plainEdge.target}!`);
    }
    const defaultMeta = this._defaultEdgeMeta;
    const edge = new Edge(plainEdge, defaultMeta, (id) => this._idsToNodes[id]);

    this._idsToEdges[edge.id] = edge;
    edge.source.outgoingEdges.push(edge);
    edge.target.incomingEdges.push(edge);
    edge.source.incidentEdges.push(edge);
    edge.target.incidentEdges.push(edge);
    return edge;
  }

  /**
   * Finds and marks edges a->b where b->a exists as well, implying node equality.
   * Also re-orders edges such that equal edges come last (useful for rendering order).
   * Mutates this.edges: When the second edge of a pair is found, it is filtered out from
   * this.edges.
   */
  _findMarkAndSortEqualEdges() {
    const lookup = {};
    this.edges = _.sortBy(_.filter(this.edges, (edge) => {
      const [l, r] = [edge.source, edge.target];
      const reverseEdge = lookup[(r.id + ',' + l.id)];
      if (reverseEdge) {
        reverseEdge.type = 'equal'; // keep the other edge
      }
      lookup[(l.id + ',' + r.id)] = edge;
      return !reverseEdge;
    }), (e) => e.type == 'equal' ? 1 : 0); // sort equal edges to last positions
  }
}

/**
 * A special implementation for executing a force layout simulation on
 * the graph was required, due to performance-degrading interactions
 * between the force layout by the d3 library and the update logic of
 * the VueJS library. When a d3 force layout is running, it stores the
 * required position and velocity data directly on the node
 * objects. It repeatedly overwrites these values several times even
 * before each single simulation step (tick) is complete. When VueJS
 * recognises changes in data, it attempts to update the visual
 * components presenting this data. Therefore, when VueJS is
 * instructed to present the same node objects that the d3 force
 * layout is working on, a significant performance hit is incurred by
 * the large amount of intermediate position data updates. Because of
 * this, we designed this class, which contains two copies of the same
 * graph: (1) a copy that VueJS presents, storing all presentational
 * data except for node positions, and (2) a copy that the force
 * layout works on, storing only nodes, edges and the force layout
 * data. These copies are then linked in the frontend code by shared
 * node and edge IDs, and the positions of the displayed nodes are
 * only updated once after each force simulation tick is
 * complete. This approach fully avoids the performance hit.
 */
class SimulatedGraph {
  /**
   * Initialize the simulation graph.
   * @param {*} graph
   * @param {*} simulation
   * @param {*} activeEdgeFilter
   * @param {*} activeNodeFilter
   */
  constructor(graph, simulation, activeEdgeFilter, activeNodeFilter) {
    this.real = Vue.reactive(graph);
    this.simulacrum = graph.plainClone();

    this._activeNodeIds = _.reduce(_.filter(this.real.nodes, activeNodeFilter), (r, node) => {
      r[node.id] = true;
      return r;
    }, {});
    this._activeEdgeIds = _.reduce(_.filter(this.real.edges, activeEdgeFilter), (r, edge) => {
      r[edge.id] = true;
      return r;
    }, {});

    this.simulacrum.setPositionsFromCCs(activeEdgeFilter, activeNodeFilter);
    simulation.stop();
    simulation.nodes(
        _.filter(this.simulacrum.nodes, (node) => this._activeNodeIds[node.id]));
    simulation.force('link').links(
        _.filter(this.simulacrum.edges, (edge) => this._activeEdgeIds[edge.id]));
    simulation.restart();
    this.simulation = simulation;
  }

  /**
   * Add the node to the simulation
   * @param {*} node
   */
  addNode(node) {
    this.real.addNode(node);
    this.simulacrum.addNode(node);
    this.simulation.nodes(this.simulacrum.nodes).restart();
  }
  /**
   * Add the edge to the simulation
   * @param {*} edge
   */
  addEdge(edge) {
    this.real.addEdge(edge);
    this.simulacrum.addEdge(edge);
    this.simulation.force('link').links(this.simulacrum.edges).restart();
  }
}

export {SimulatedGraph, Graph, Node, Edge};
