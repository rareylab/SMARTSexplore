/* Author: Simon Welker */
import _ from 'lodash';
import {Node, Edge, Graph, SimulatedGraph} from '../../src/components/graphComponents/graph.js';

const nodeData = {
  id: 1,
  name: 'xyz',
  pattern: 'C',
  library: 'test',
};
const nodeData2 = {
  ...nodeData,
  id: 2,
  pattern: 'CC',
};
const edgeData = {
  id: 1,
  mcssim: 0.3,
  spsim: 0.1,
  type: 'subset',
  source: 1,
  target: 2,
};

describe('Node', () => {
  it('stores id, name, pattern and library', () => {
    const node = new Node(nodeData);
    expect(node.id).toEqual(nodeData.id);
    expect(node.name).toEqual(nodeData.name);
    expect(node.pattern).toEqual(nodeData.pattern);
    expect(node.library).toEqual(nodeData.library);
  });

  it('does not store just any arbitrary parameter as an attribute', () => {
    const node = new Node({...nodeData, bongodrum: true});
    expect(node.bongodrum).toBeUndefined();
  });

  it('requires a nonempty pattern string', () => {
    expect(() => {
      new Node({...nodeData, pattern: undefined});
    }).toThrow();
    expect(() => {
      new Node({...nodeData, pattern: ''});
    }).toThrow();
  });

  it('does not require a nonempty name or library', () => {
    expect(() => {
      new Node({...nodeData, library: ''});
      new Node({...nodeData, library: null});
      new Node({...nodeData, name: ''});
      new Node({...nodeData, name: null});
    }).not.toThrow();
  });

  it('stores empty arrays for outgoing, incoming and incident edges', () => {
    const node = new Node(nodeData);
    expect(node.outgoingEdges).toBeInstanceOf(Array);
    expect(node.incomingEdges).toBeInstanceOf(Array);
    expect(node.incidentEdges).toBeInstanceOf(Array);
  });

  it('has a metadata dictionary property', () => {
    const node = new Node(nodeData);
    expect(node.meta).toBeInstanceOf(Object);
  });

  it('assigns metadata from the defaultMeta parameter', () => {
    const node = new Node(nodeData, {test3000: true});
    expect(node.meta.test3000).toBe(true);
  });

  it('does not just copy metadata from defaultMeta but deep-clones it', () => {
    const arr = [];
    const node = new Node(nodeData, {array123: arr});
    expect(node.meta.array123).not.toBe(arr);

    arr.push(300, 400);
    expect(arr.length).toEqual(2);
    expect(node.meta.array123.length).toEqual(0);

    node.meta.array123.push(1, 2, 3);
    expect(arr.length).toEqual(2);
    expect(node.meta.array123.length).toEqual(3);
  });
});


describe('Edge', () => {
  it('stores id, mcssim, spsim, type, source and target', () => {
    const edge = new Edge(edgeData);
    ['id', 'mcssim', 'spsim', 'type', 'source', 'target'].forEach((attr) => {
      expect(edge[attr]).toEqual(edgeData[attr]);
    });
  });

  it('does not store just any arbitrary parameter as an attribute', () => {
    const edge = new Edge({...edgeData, bongodrum: true});
    expect(edge.bongodrum).toBeUndefined();
  });

  it('has a metadata dictionary property', () => {
    const edge = new Edge(edgeData);
    expect(edge.meta).toBeInstanceOf(Object);
  });

  it('requires the type to be "equal" or "subset" if type is truthy', () => {
    expect(() => {new Edge({...edgeData, type: 'blah'})}).toThrow();
    expect(() => {new Edge({...edgeData, type: 300})}).toThrow();
    expect(() => {new Edge({...edgeData, type: ['equal']})}).toThrow();
    expect(() => {new Edge({...edgeData, type: 'equal'})}).not.toThrow();
    expect(() => {new Edge({...edgeData, type: 'subset'})}).not.toThrow();
  });

  it('sets the type to "subset" by default if type is falsy', () => {
    expect(() => {new Edge({...edgeData, type: null})}).not.toThrow();

    _.each([null, false, undefined], (type) => {
      const edge = new Edge({...edgeData, type: type});
      expect(edge.type).toEqual('subset');
    });
  });

  it('requires mcssim and spsim to be numbers between 0 and 1', () => {
    expect(() => {new Edge(edgeData)}).not.toThrow();

    _.each([null, 'xy', undefined, [], 1.01, 1.00001, -1.01, 1.00001, 1+1e-3, -1-1e-3],
        (val) => {
          expect(() => {
            new Edge({...edgeData, mcssim: val});
          }).toThrow();
          expect(() => {
            new Edge({...edgeData, spsim: val});
          }).toThrow();
        });

    _.each([0, 1, 0.5, 0.1, 0.99999, -0.0], (val) => {
      expect(() => {
        new Edge({...edgeData, mcssim: val});
      }).not.toThrow();
      expect(() => {
        new Edge({...edgeData, spsim: val});
      }).not.toThrow();
    });
  });

  it('assigns metadata from the defaultMeta parameter', () => {
    const edge = new Edge(edgeData, {test3000: true});
    expect(edge.meta.test3000).toBe(true);
  });

  it('does not just copy metadata from defaultMeta but deep-clones it', () => {
    const arr = [];
    const edge = new Edge(edgeData, {array123: arr});
    expect(edge.meta.array123).not.toBe(arr);

    arr.push(300, 400);
    expect(arr.length).toEqual(2);
    expect(edge.meta.array123.length).toEqual(0);

    edge.meta.array123.push(1, 2, 3);
    expect(arr.length).toEqual(2);
    expect(edge.meta.array123.length).toEqual(3);
  });

  it('reassigns source/target from the original values if passed a getNodeFn function', () => {
    const nodeA = new Node(nodeData);
    const nodeB = new Node(nodeData2);
    const myGetNodeFn = (id) => {
      if (id == nodeData.id) return nodeA;
      else if (id == nodeData2.id) return nodeB;
      else {throw new Error("myGetNodeFn was given an unknown id");}
    };

    const nodeABEdgeData = {...edgeData, source: nodeA.id, target: nodeB.id};

    const edge = new Edge(
        nodeABEdgeData,
        {}, // empty defaultMeta
        myGetNodeFn,
    );
    expect(edge.source).toBe(nodeA);
    expect(edge.target).toBe(nodeB);

    const edgeNoGetNodeFn = new Edge(
        nodeABEdgeData,
        {}, // empty defaultMeta
        null,
    );
    expect(edgeNoGetNodeFn.source).not.toBe(nodeA);
    expect(edgeNoGetNodeFn.target).not.toBe(nodeB);
    expect(edgeNoGetNodeFn.source).toBe(nodeData.id);
    expect(edgeNoGetNodeFn.target).toBe(nodeData2.id);
  });
});


describe('Graph', () => {
  const iMin = 1;
  const iMax = 10;
  const iRange = _.range(iMin, iMax);

  let nodes;
  let edges;
  beforeEach(() => {
    // set up a chain of aliphatic chains :D
    nodes = _.map(iRange, (i) => {
      return {
        id: i,
        name: 'C'+i,
        pattern: _.repeat('C', i),
        library: 'aliphatic',
      };
    });
    edges = _.flatMap(iRange, (i) => {
      return _.map(_.range(1, i), (j) => {
        return {
          id: i*iMax + j,
          mcssim: 0.1,
          spsim: 0.1,
          source: i,
          target: j,
          type: 'subset',
        };
      });
    });
  });

  it('constructs a graph of Node and Edge instances from plain-object descriptions', () => {
    const graph = new Graph(nodes, edges);
    expect(graph.nodes.length).toEqual(nodes.length);
    expect(graph.edges.length).toEqual(edges.length);
    _.each(graph.nodes, (node) => {expect(node).toBeInstanceOf(Node);});
    _.each(graph.edges, (edge) => {expect(edge).toBeInstanceOf(Edge);});
  });

  it('stores a deep copy of default node meta and default edge meta on each node/edge', () => {
    const arr = [];
    const graph = new Graph(nodes, edges,
        {isANode: true, arr: arr},
        {isAnEdge: true, arr: arr},
    );

    _.each(graph.nodes, (node) => {
      expect(node.meta.isANode).toBe(true);
      expect(node.meta.isAnEdge).toBeFalsy();
      expect(node.meta.arr).toBeInstanceOf(Array);
      expect(node.meta.arr).not.toBe(arr);
    });
    _.each(graph.edges, (edge) => {
      expect(edge.meta.isAnEdge).toBe(true);
      expect(edge.meta.isANode).toBeFalsy();
      expect(edge.meta.arr).toBeInstanceOf(Array);
      expect(edge.meta.arr).not.toBe(arr);
    });
  });

  it('replaces <- and -> edges by one <-> edge with type "equal", iff markEqualEdges is true', () => {
    const duplicateNode = {...nodes[0], library: 'different-lib'};
    const nodesWithDuplicate = [...nodes, duplicateNode];
    const edgesWithImpliedEqualEdge = [
      ...edges,
      {...edgeData, id: 10000, source: nodes[0].id, target: duplicateNode.id},
      {...edgeData, id: 10001, source: duplicateNode.id, target: nodes[0].id},
    ];

    const graph = new Graph(
        nodesWithDuplicate, edgesWithImpliedEqualEdge, {}, {}, true);
    const graphNoEqual = new Graph(
        nodesWithDuplicate, edgesWithImpliedEqualEdge, {}, {}, false);

    expect(graph.edges.length).toBe(edges.length + 1);
    expect(graphNoEqual.edges.length).toBe(edges.length + 2);

    expect(_.find(graph.edges, {type: 'equal'})).toBeTruthy();
    expect(_.filter(graph.edges, {type: 'equal'}).length).toBe(1);
    expect(_.find(graphNoEqual.edges, {type: 'equal'})).toBeFalsy();
  });

  it('can retrieve nodes and edges given their IDs', () => {
    const graph = new Graph(nodes, edges);

    _.each(nodes, (node) => {
      expect(graph.getNodeById(node.id)).toBeTruthy();
      expect(graph.getNodeById(node.id).name).toEqual(node.name);
    });
    _.each(edges, (edge) => {
      expect(graph.getEdgeById(edge.id)).toBeTruthy();
      expect(graph.getEdgeById(edge.id).name).toEqual(edge.name);
    });
  });

  it('can return a clone whose nodes and edges are distinct objects from the originals', () => {
    const graph = new Graph(nodes, edges);
    graph.nodes[0].meta.test = 300;
    const clone = graph.plainClone();

    expect(clone.nodes[0].meta.test).toBeUndefined();
    expect(graph.nodes[0].meta.test).toEqual(300);

    _.each(graph.nodes, (node) => {
      const cloneNode = clone.getNodeById(node.id);

      expect(cloneNode).toBeInstanceOf(Node);
      expect(cloneNode.name).toEqual(node.name);
      expect(cloneNode).not.toBe(node);

      cloneNode.xyz = 3;
      node.abc = 4;
      expect(node.xyz).toBeUndefined();
      expect(cloneNode.abc).toBeUndefined();
    });

    _.each(graph.edges, (edge) => {
      const cloneEdge = clone.getEdgeById(edge.id);

      expect(cloneEdge).toBeTruthy();
      expect(cloneEdge.name).toEqual(edge.name);
      expect(cloneEdge).not.toBe(edge);

      cloneEdge.xyz = 3;
      edge.abc = 4;
      expect(edge.xyz).toBeUndefined();
      expect(cloneEdge.abc).toBeUndefined();
    });
  });

  describe('DFS', () => {
    let graph;
    let firstNode, lastNode, rootNode;
    let toRootEdge, fromRootEdge;
    let cb, cbById;

    beforeEach(() => {
      firstNode = nodes[0];
      lastNode = nodes[nodes.length-1];
      rootNode = {id: 42000, name: 'root', pattern: 'XYZ', library: 'root'};
      toRootEdge = {...edgeData, id: 10000, source: firstNode.id, target: rootNode.id};
      fromRootEdge = {...edgeData, id: 10001, source: rootNode.id, target: lastNode.id};

      // graph with additional node that first node is subset of,
      // and that is subset of second node,
      // but not anything else
      const nodesPlusRoot = [...nodes, rootNode];
      const edgesPlusRootEdges = [...edges, toRootEdge, fromRootEdge];
      graph = new Graph(nodesPlusRoot, edgesPlusRootEdges);

      cb = jest.fn();
      cbById = (node, depth) => cb(node.id, depth);
    });

    it('can run from one start node', () => {
      graph.runDFS(graph.nodes[0], 'outgoing', 1);
    });

    it('can run from multiple start nodes', () => {
      graph.runDFS([graph.nodes[0], graph.nodes[1]], 'outgoing', 1);
    });

    it('does not accept non-nodes as start node or start nodes', () => {
      _.each([null,
        new Edge(edgeData),
        [new Node(nodeData), null],
        [new Edge(edgeData)]],
      (val) => {
        expect(() => {graph.runDFS(val, 'outgoing', 1);}).toThrow();
      });
    });

    it('does not accept a foreign node (node with unknown ID) as start node', () => {
      expect(() => {
        graph.runDFS(new Node({...nodeData, id: 1235616}), 'outgoing', 1);
      }).toThrow();
    });

    describe('given a node callback fn', () => {
      it('visits the root node first', () => {
        graph.runDFS(graph.getNodeById(rootNode.id), 'all', 1, cbById);
        expect(cb).toHaveBeenNthCalledWith(1, rootNode.id, 0);
      });

      it('visits nodes correctly in "incoming" mode', () => {
        graph.runDFS(graph.getNodeById(rootNode.id), 'incoming', 1, cbById);
        expect(cb).toHaveBeenCalledTimes(2);
        expect(cb).toHaveBeenCalledWith(rootNode.id, 0);
        expect(cb).toHaveBeenCalledWith(firstNode.id, 1);
      });

      it('visits nodes correctly in "outgoing" mode', () => {
        graph.runDFS(graph.getNodeById(rootNode.id), 'outgoing', 1, cbById);
        expect(cb).toHaveBeenCalledTimes(2);
        expect(cb).toHaveBeenCalledWith(rootNode.id, 0);
        expect(cb).toHaveBeenCalledWith(lastNode.id, 1);
      });

      it('visits nodes correctly in "all" mode', () => {
        graph.runDFS(graph.getNodeById(rootNode.id), 'all', 1, cbById);
        expect(cb).toHaveBeenCalledTimes(3);
        expect(cb).toHaveBeenCalledWith(rootNode.id, 0);
        expect(cb).toHaveBeenCalledWith(firstNode.id, 1);
        expect(cb).toHaveBeenCalledWith(lastNode.id, 1);
      });

      it('visits nodes correctly in "all" mode for depth=2', () => {
        graph.runDFS(graph.getNodeById(rootNode.id), 'outgoing', 2, cbById);
        // all nodes should have been visited -- the +1 is for the 'root node'
        expect(cb).toHaveBeenCalledTimes(nodes.length + 1);
      });

      it('hands over a reference to the real node instance and not a copy', () => {
        graph.runDFS(
            graph.getNodeById(rootNode.id),
            'incoming', Infinity, (node) => {
              node.TESTOMATIKO = 42;
            });

        expect(_.find(graph.nodes, {TESTOMATIKO: 42})).toBeTruthy();
        expect(_.find(graph.edges, {TESTOMATIKO: 42})).toBeFalsy();
      });
    });

    describe('given an edge callback fn', () => {
      it('traverses only outgoing edges if in outgoing mode', () => {
        graph.runDFS(
            graph.getNodeById(rootNode.id),
            'outgoing', Infinity, null, cbById);

        expect(cb).toHaveBeenCalledWith(expect.anything(), true);
        expect(cb).not.toHaveBeenCalledWith(expect.anything(), false);
      });

      it('traverses only incoming edges if in incoming mode', () => {
        graph.runDFS(
            graph.getNodeById(rootNode.id),
            'incoming', Infinity, null, cbById);

        expect(cb).toHaveBeenCalledWith(expect.anything(), false);
        expect(cb).not.toHaveBeenCalledWith(expect.anything(), true);
      });

      it('hands over a reference to the real edge instance and not a copy', () => {
        graph.runDFS(
            graph.getNodeById(rootNode.id),
            'incoming', Infinity, null, (edge) => {
              edge.TESTOMATIKO = 42;
            });

        expect(_.find(graph.edges, {TESTOMATIKO: 42})).toBeTruthy();
        expect(_.find(graph.nodes, {TESTOMATIKO: 42})).toBeFalsy();
      });
    });

    it('traverses only edges fulfilling the edgeFilter predicate, if given', () => {
      graph.runDFS(
          graph.getNodeById(lastNode.id),
          'outgoing', Infinity,
          null, cbById,
          null,
          // only visit along "neighboring" nodes in the original C, CC, CCC, ... chain
          (edge) => edge.source.id == edge.target.id + 1);
      // should be N-1 calls in this chain
      expect(cb).toHaveBeenCalledTimes(nodes.length - 1);
    });

    it('visits only nodes fulfilling the nodeFilter predicate, if given', () => {
      graph.runDFS(
          graph.getNodeById(2),
          'all', Infinity,
          cbById, null,
          null,
          // only visit nodes which have even amount of 'C' in their pattern
          null, (node) => {
            return _.countBy(node.pattern, (char) => char == 'C')[true] % 2 == 0
          });
      expect(cb).toHaveBeenCalledTimes(Math.floor(nodes.length / 2));
    });
  });

  describe('getCCs', () => {
    describe('on a two-clique two-CC example graph', () => {
      let nodesA, nodesB, edgesA, edgesB, graph;

      beforeEach(() => {
        nodesA = _.map(_.range(0, 4), (i) => {
          return {...nodeData, id: i};
        });
        nodesB = _.map(_.range(5, 10), (i) => {
          return {...nodeData, id: i};
        });

        edgesA = _.map(_.range(0, 4**2), (k) => { // 4-clique
          const i = k % 4;
          const j = Math.floor(k / 4);
          return {...edgeData, id: k, source: i, target: j};
        });
        edgesB = _.map(_.range(0, 5**2), (k) => { // 5-clique
          const i = 5 + (k % 5);
          const j = 5 + (Math.floor(k / 5));
          return {...edgeData, id: k, source: i, target: j};
        });
      });

      it('correctly calculates the two CCs of the graph', () => {
        graph = new Graph([...nodesA, ...nodesB], [...edgesA, ...edgesB]);
        const [ccs, nodeToCC] = graph.getCCs();
        expect(ccs.length).toEqual(2);

        const A_CCs = _.map(nodesA, (node) => nodeToCC[node.id]);
        const B_CCs = _.map(nodesB, (node) => nodeToCC[node.id]);
        expect(A_CCs[0]).toEqual(expect.anything());
        expect(B_CCs[0]).toEqual(expect.anything());
        expect(_.every(A_CCs, cc => cc == A_CCs[0])).toBe(true);
        expect(_.every(B_CCs, cc => cc == B_CCs[0])).toBe(true);
        expect(A_CCs[0]).not.toEqual(B_CCs[0]);
      });

      it('correctly calculates one CC when adding a single connecting edge', () => {
        const connectingEdgeAB = {
          ...edgeData, id: 10000,
          source: nodesA[0].id,
          target: nodesB[0].id,
        };
        const connectingEdgeBA = {
          ...edgeData, id: 10000,
          source: nodesB[0].id,
          target: nodesA[0].id,
        };

        _.each([connectingEdgeAB, connectingEdgeBA], (connectingEdge) => {
          graph = new Graph(
              [...nodesA, ...nodesB],
              [...edgesA, ...edgesB, connectingEdge]
          );
          const [ccs, nodeToCC] = graph.getCCs();
          expect(ccs.length).toEqual(1);

          const A_CCs = _.map(nodesA, (node) => nodeToCC[node.id]);
          const B_CCs = _.map(nodesB, (node) => nodeToCC[node.id]);
          expect(A_CCs[0]).toEqual(expect.anything());
          expect(B_CCs[0]).toEqual(expect.anything());
          expect(_.every(A_CCs, cc => cc == A_CCs[0])).toBe(true);
          expect(_.every(B_CCs, cc => cc == A_CCs[0])).toBe(true);
        });
      });
    });
  });
});
