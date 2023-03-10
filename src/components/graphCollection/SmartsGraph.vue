<template>
<svg ref="graphSvg" width="100%" height="100%" @click.self="handleBackgroundClick">
    <defs>
        <ArrowheadMarkers :colors="edgeColorFn.colors" />
    </defs>
    <g ref="graphSvgMasterGroup" @click.self="handleBackgroundClick">
        <SmartsSubsetEdges :edges="activeEdges"
            :classFn="edgeClassFn"
            :colorFn="edgeColorFn"
            :styleFn="edgeStyleFn"
            @edgeClick="$emit('edgeClick', $event)"
            @edgeHover="$emit('edgeHover', $event)"
            @click.self="handleBackgroundClick"
        />
        <SmartsNodes :nodes="activeNodes"
            :classFn="nodeClassFn_"
            :colorFn="nodeColorFn"
            :styleFn="nodeStyleFn"
            @nodeClick="$emit('nodeClick', $event)"
            @nodeHover="$emit('nodeHover', $event)"
            @nodeDblClick="handleNodeDblClick($event)"
            @nodeDrag="handleNodeDrag"
            @nodeDragStart="handleNodeDragStart"
            @nodeDragEnd="handleNodeDragEnd"
            @click.self="handleBackgroundClick"
        />
    </g>
</svg>
</template>

<script>
/* eslint max-len: */
import ArrowheadMarkers from '../graphComponents/ArrowheadMarkers.vue';
import SmartsNodes from '../graphComponents/SmartsNodes.vue';
import SmartsSubsetEdges from '../graphComponents/SmartsSubsetEdges.vue';
import {Graph, SimulatedGraph} from '../graphComponents/graph.js';

import * as d3ScaleChromatic from 'd3-scale-chromatic';
import * as d3Interpolate from 'd3-interpolate';
import * as d3Scale from 'd3-scale';
import * as d3Or from 'd3';
import * as d3Reuse from 'd3-force-reuse';
import * as d3Sampled from 'd3-force-sampled';
const d3 = Object.assign({}, d3Or, d3Reuse, d3ScaleChromatic, d3Interpolate, d3Scale, d3Sampled);

const perObjectFn = {
  type: Function,
  validator: (fn) => fn.length == 1,
};

/**
 * Hacky function for getting the ID of either an HTML element representing a SMARTS node or edge,
 * or an object representing a SMARTS node or edge. Required to be this way so that it can be
 * passed to d3-force as is.
 * @param {Object} obj a Node, Edge, or corresponding HTML element of either of these
 * @return {id} The unique ID associated with the given obj
 */
function getId(obj) {
  // eslint-disable-next-line no-invalid-this
  return obj ? obj.id : this.dataset.id;
}

export default {
  name: 'SmartsGraph',
  emits: ['edgeClick', 'nodeClick', 'edgeHover', 'nodeHover', 'backgroundClick'],
  components: {
    ArrowheadMarkers, SmartsNodes, SmartsSubsetEdges,
  },
  /** The props of this component. */
  props: {
    /** The Graph instance to render */
    graph: Graph,
    /**
     * A function that returns a (CSS class) -> (boolean) mapping given a node.
     * Only if the boolean is true, the class will be added to the node.
     * No classes by default.
     */
    nodeClassFn: {...perObjectFn, default: (node) => {}},
    /** A function that returns a color given a node (white by default). */
    nodeColorFn: {...perObjectFn, default: (node) => 'white'},
    /**
     * A function that returns a (key)->(value) CSS style mapping given a node.
     * No styles by default
     */
    nodeStyleFn: {...perObjectFn, default: (node) => {}},
    /**
     * A function that determines if a node is active
     * (shown, included in the layout and force simulation, visited during DFS)
     */
    nodeActiveFn: {...perObjectFn, default: (node) => true},

    /**
     * A function that returns a (CSS class) -> (boolean) mapping given an edge.
     * Only if the boolean is true, the class will be added to the edge.
     * No classes by default.
     */
    edgeClassFn: {...perObjectFn, default: (node) => {}},
    /** A function that returns a color given a node (black by default). */
    edgeColorFn: {
      ...perObjectFn,
      default: (edge) => 'black',
      validator: (fn) => fn.length == 1 && fn.colors instanceof Array,
    },
    /**
     * A function that returns a (key)->(value) CSS style mapping given an edge.
     * No styles by default
     */
    edgeStyleFn: {...perObjectFn, default: (edge) => {}},
    /**
     * A function that determines if an edge is active
     * (shown, included in the layout and force simulation, traversed during DFS)
     */
    edgeActiveFn: {...perObjectFn, default: (edge) => true},
  },
  data() {
    return {
      tickCounter: 0,
      isObjectSelectionFixed: false,
    };
  },
  /** Computed props of this component */
  computed: {
  /**
   * The currently active edges (determined by the edgeActiveFn prop)
   * @return {edges}
   */
    activeEdges() {
      return _.filter(this.graph.edges, this.edgeActiveFn);
    },
    /**
     * The currently active nodes (determined by the nodeActiveFn prop)
     * @return {nodes}
    */
    activeNodes() {
      return _.filter(this.graph.nodes, this.nodeActiveFn);
    },
    /**
     * Merges external nodeClassFn behavior with component-internal behavior
     *  @return {class}
     */
    nodeClassFn_() {
      return (node) => {
        return {...this.nodeClassFn(node), 'node-fixed': node.__dragFixed};
      };
    },
  },
  /**
   * The methods of this component
   */
  methods: {
    /**
     * Initialize the graph simulation and return the SimulatedGraph instance
     * @return {sgraph}
     */
    initGraphSimulation() {
      this.initSimulation();
      this._simulatedGraph = new SimulatedGraph(
          this.graph, this._simulation, this.edgeActiveFn, this.nodeActiveFn,
      );
      return this._simulatedGraph;
    },
    /**
     * Set up and store a simulation with the devised forces and parameters.
     */
    initSimulation() {
      if (this._simulation) {
        this._simulation.stop();
      }
      this._simulation = d3.forceSimulation()
          // .velocityDecay(0.2)
          .force('charge', d3.forceManyBody()
              // .updateSize(function(nodes) {
              //   return Math.pow(nodes.length, 0.25);
              // })
              // .sampleSize(function(nodes) {
              //   return Math.pow(nodes.length, 0.75);
              // })
              // .chargeMultiplier(function(nodes) {
              //   return 1;
              // })
              .strength((node) => {
                return -30 * Math.log(1 + node.incidentEdges.length); // -30
              }))
          .force('link', d3.forceLink()
              .id((edge) => edge.id)
              .distance((edge) => edge.type === 'equal' ? 75 : 150)
              .strength(1) // 1
              .iterations(3)) // 3
          .force('collision', d3.forceCollide()
              .radius(22.5)) // 22.5
          .on('tick', this.onSimulationTick.bind(this));
      // implicitly use restartSimulation's default values for alpha & alphaDecay
      this.restartSimulation();
    },
    /**
     * Restart the simulation, optionally setting a new alpha and alphaDecay.
     * @param {Number} alpha The 'temperature' of the simulation (see d3-force docs)
     * @param {Number} alphaDecay The 'temperature decay speed' of the simulation (see d3-force)
     */
    restartSimulation(alpha = 2, alphaDecay = 0.15) {
      this._simulation.alpha(alpha).alphaDecay(alphaDecay).restart();
    },
    /**
     * Runs on each tick of the force simulation. Updates node and edge positions efficiently.
     * Note that this function somewhat bypasses Vue render logic and only works when the getId
     * function is ensured to work properly to link up exactly the correct nodes with exactly
     * the correct SMARTS objects.
     */
    onSimulationTick() {
      // console.log(this._simulatedGraph.simulacrum.nodes[0]);
      const root = d3.select(this.$refs.graphSvg);
      // update node positions
      root.selectAll('circle.node').data(this._simulatedGraph.simulacrum.nodes, getId) // this._simulatedGraph.simulacrum.nodes // this.graph.nodes
          .attr('cx', (node) => node.x)
          .attr('cy', (node) => node.y);
      // update edge positions (real and hoverhelper edges)
      _.each(['line.subset.real', 'line.subset.hoverhelper'], (selector) => {
        root.selectAll(selector).data(this._simulatedGraph.simulacrum.edges, getId) // this._simulatedGraph.simulacrum.edges //this.graph.nodes
            .attr('x1', (edge) => edge.source.x)
            .attr('x2', (edge) => edge.target.x)
            .attr('y1', (edge) => edge.source.y)
            .attr('y2', (edge) => edge.target.y);
      });
      this.tickCounter = this.tickCounter +1;
    },

    /**
     * Sets up panning & zooming for the graph.
     */
    initGraphZoom() {
      const graphSvgElement = this.$refs.graphSvg;
      const masterGroupElement = d3.select(this.$refs.graphSvgMasterGroup);
      const zoom = d3.zoom().scaleExtent([0.1, 2]);
      const initialScale = 0.25;
      const width = graphSvgElement.clientWidth; // 1280*2//graphSvgElement.clientWidth;
      const height = graphSvgElement.clientHeight; // 640*2//graphSvgElement.clientHeight;
      d3.select(graphSvgElement)
          .call(zoom
              .on('zoom', (event) => masterGroupElement.attr('transform', event.transform)))
          .on('dblclick.zoom', null)
          .call(zoom.scaleTo, initialScale)
          .call(zoom.translateTo, -width/2 * initialScale, -height/2 * initialScale);
    },

    /**
     * Handles the user dragging a node, by removing nodes that are not in the same CC from the
     * force simulation. Improves responsiveness.
     * @param {event} event
     */
    handleNodeDragStart(event) {
      const node = event.node;
      const id = node.id;
      // const { id } = node;
      const {simulacrum} = this._simulatedGraph;
      const simNode = simulacrum.getNodeById(id);
      // Only include nodes in the same connected component in the simulation while dragging,
      // to improve responsiveness
      const ccNodes = [];
      const ccEdges = [];
      this._simulatedGraph.simulacrum.runDFS(
          simNode, 'all', Infinity,
          (node) => {
            ccNodes.push(node);
          },
          (edge) => {
            ccEdges.push(edge);
          },
          null,
          this.edgeActiveFn);

      this._prevSimNodes = this._simulation.nodes();
      this._simulation.nodes(ccNodes);
      this._prevSimEdges = this._simulation.force('link').links();
      this._simulation.force('link').links(ccEdges);
    },
    /** Handles the user dragging a node, by taking its dragged position as fixed.
    * @param {event} event
    */
    handleNodeDrag(event) {
      const myEvent = event.event;
      const x = myEvent.x;
      const y = myEvent.y;

      const node = event.node;
      const id = node.id;
      const {simulacrum} = this._simulatedGraph;
      const simNode = simulacrum.getNodeById(id);

      node.__dragFixed = true;
      simNode.fx = x;
      simNode.fy = y;
      this.restartSimulation(2, 0.15);
    },
    /**
     * Handles the user stopping to drag a node, by resetting the choice of nodes currently
     * active in the force simulation
     * @param {event} event
     */
    handleNodeDragEnd(event) {
      if (this._prevSimNodes) {
        this._simulation.nodes(this._prevSimNodes);
        delete this._prevSimNodes;
      }
      if (this._prevSimEdges) {
        this._simulation.force('link').links(this._prevSimEdges);
        delete this._prevSimEdges;
      }
    },
    /**
     * Handles the user double-clicking a node, by unfixing it
     */
    handleNodeDblClick({node, event}) {
      const {id} = node;
      const {simulacrum} = this._simulatedGraph;
      const simNode = simulacrum.getNodeById(id);

      node.__dragFixed = false;
      delete simNode.fx;
      delete simNode.fy;
      this.restartSimulation(0.05, 0.05);
    },
    /**
     * Emits an event when the user clicks on the background.
     *  @param {event} event
     */
    handleBackgroundClick(event) {
      this.$emit('backgroundClick', event);
    },
  },
  /**
   * Sets up a watcher to reinitialize the graph simulation if the graph or the active edges
   * change (not deep-watching, so only triggers when these are replaced)
   */
  beforeMount() {
    this.$watch(() => [this.graph, this.activeEdges], (newVal) => {
      this.initGraphSimulation();

      // this.restartSimulation(2, 0.01);
      // this.onSimulationTick();
      // const start = new Date();
      // this._simulation.tick(100);
      // const time = new Date() - start;
      // console.log(time);
      // console.log(this.tickCounter);


      this.tickCounter= 0;
      this.restartSimulation(2, 0.15);
      const start = new Date;
      setTimeout(() => {
        const time = new Date() - start;
        console.log('time1', time);
        console.log('tick', this.tickCounter);
        console.log('time2', time);
      }, 1000);
      // setTimeout(() => {
      //   const time = new Date() - start;
      //   console.log('time', time);
      //   this._simulation.stop();
      // }, 2000);
    }, {immediate: true});
  },
  /**
   * Sets up the zoom functionality for the graph
   */
  mounted() {
    this.initGraphZoom();
  },
  beforeUnmount() {
    const graphSvgM = this.$refs.graphSvgMasterGroup;
    graphSvgM.remove();
  },
};

</script>

<style>
.hidden {
    display: none !important;
}
</style>
