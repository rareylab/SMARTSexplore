import _ from 'lodash';

import * as d3Force from 'd3-force';
import * as d3Drag from 'd3-drag';
import * as d3Selection from 'd3-selection';
import * as d3Zoom from 'd3-zoom';
const d3 = Object.assign({}, d3Force, d3Drag, d3Selection, d3Zoom);

import { SimulatedGraph, Graph } from '../graph.js'

/**
 * Hacky function for getting the ID of either an HTML element representing a SMARTS node or edge,
 * or an object representing a SMARTS node or edge. Required to be this way so that it can be
 * passed to d3-force as is.
 * @param {Object} obj a Node, Edge, or corresponding HTML element of either of these
 * @returns The unique ID associated with the given obj
 */
function getId(obj) {
    return obj ? obj.id : this.dataset.id;
}

/**
 * Gets an HTML id from a given color. Only works properly for colors in hex format.
 * Behavior is undefined for other color formats.
 *
 * Used to link up ArrowheadMarkers and SmartsEdges.
 * @param {String} color The color to use.
 * @returns The HTML id that can be attached to an element.
 */
function getColorIdFromColor(color) {
    return color.substring(1);
}

/**
 * Vue component that renders an SVG marker for an arrowhead.
 * Used implicitly by the SmartsSubsetEdge component.
 */
const ArrowheadMarker = {
    name: 'ArrowheadMarker',
    props: {
        color: {
            type: String,
            default: () => ''
        },
        refX: {
            type: Number,
            default: () => 14
        },
        size: {
            type: Number,
            default: () => 25
        },
        id: {
            type: String
        }
    },
    template: `
<marker
    :id="id" :refX="refX" refY="0" viewBox="0 -5 10 10"
    markerUnits="userSpaceOnUse" :markerWidth="size" :markerHeight="size"
    xoverflow="visible" orient="auto"
>
    <path d="M 0,-5 L 10,0 L 0,5 z" :fill="color" />
</marker>`
};


/**
 * Vue component that renders multiple SVG markers for an arrowhead, given a set of colors.
 * Used implicitly by the SmartsSubsetEdge component.
 */
const ArrowheadMarkers = {
    name: 'ArrowheadMarkers',
    components: { ArrowheadMarker },
    props: {
        colors: {
            type: Array,
            validator: (colors) => {
                return _.every(colors, (color) => color.startsWith('#'));
            }
        }
    },
    computed: {
        ids() {
            return _.fromPairs(
                _.map(this.colors,
                    (color) => [color, `arrowhead-${getColorIdFromColor(color)}`]
            ));
        }
    },
    template: `
<arrowhead-marker v-for="color in colors"
    :color="color"
    :id="ids[color]"
/>`
};


/**
 * Vue component that renders a single SMARTS node.
 */
const SmartsNode = {
    name: 'SmartsNode',
    emits: ['nodeDrag', 'nodeDragStart', 'nodeDragEnd'],
    props: {
        node: Object,
        classFn: Function,
        colorFn: Function,
        styleFn: Function
    },
    mounted() {
        const nodeDrag = d3.drag();
        nodeDrag
            .on("drag", (event) => this.$emit('nodeDrag', { event: event, node: this.node }))
            .on("start", (event) => this.$emit('nodeDragStart', { event: event, node: this.node }))
            .on("end", (event) => this.$emit('nodeDragEnd', { event: event, node: this.node}));
        d3.select(this.$refs.node).call(nodeDrag);
    },
    template: `
<circle
    ref="node"
    class="node"
    :class="classFn(node)"
    r="15"
    :fill="colorFn(node)"
    :style="styleFn(node)"
/>
`
};


/**
 * Vue component that renders a collection of SMARTS nodes.
 */
const SmartsNodes = {
    name: 'SmartsNodes',
    components: { SmartsNode },
    emits: ['nodeClick', 'nodeHover', 'nodeDblClick', 'nodeDrag', 'nodeDragStart', 'nodeDragEnd'],
    props: {
        nodes: Array,
        classFn: Function,
        colorFn: Function,
        styleFn: Function
    },
    template: `
<g class="smarts-nodes">
    <smarts-node
        v-for="node in nodes"
        :key="node.id"
        :data-id="node.id"
        :node="node"
        :classFn="classFn"
        :colorFn="colorFn"
        :styleFn="styleFn"
        @click="$emit('nodeClick', { event: $event, node: node })"
        @dblclick="$emit('nodeDblClick', { event: $event, node: node })"
        @mouseover="$emit('nodeHover', { event: $event, node: node })"
        @nodeDrag="$emit('nodeDrag', $event)"
        @nodeDragStart="$emit('nodeDragStart', $event)"
        @nodeDragEnd="$emit('nodeDragEnd', $event)"
    />
</g>
`,
};


/**
 * Vue component that renders a single directed SMARTS subset edge.
 */
const SmartsSubsetEdge = {
    name: 'SmartsSubsetEdge',
    props: {
        edge: Object,
        classFn: Function,
        colorFn: Function,
        styleFn: Function
    },
    template: `
<g class="composite-line" :class="classFn(edge)">
    <line ref="lineHelper"
        class="edge subset hoverhelper"
        stroke="black"
        :stroke-width="20"
        :data-id="edge.id" />
    <line ref="lineReal"
        class="edge subset real"
        :marker-end="markerEnd"
        :stroke="colorFn(edge)"
        :style="styleFn(edge)"
        :data-id="edge.id" />
</g>
`,
    computed: {
        markerEnd: function() {
            if(this.edge.type === 'equal') return '';
            else {
                const colorId = getColorIdFromColor(this.colorFn(this.edge));
                return `url(#arrowhead-${colorId})`;
            }
        }
    }
};

/**
 * Vue component that renders a collection of directed SMARTS subset edges.
 */
const SmartsSubsetEdges = {
    name: 'SmartsSubsetEdges',
    components: { SmartsSubsetEdge },
    emits: ['edgeHover', 'edgeClick'],
    props: {
        edges: Object,
        classFn: Function,
        colorFn: Function,
        styleFn: Function
    },
    template: `
<g class="subset-edges">
    <smarts-subset-edge v-for="edge in edges"
        :key="edge.id"
        :edge="edge"
        :classFn="classFn"
        :colorFn="colorFn"
        :styleFn="styleFn"
        @mouseover="$emit('edgeHover', { event: $event, edge: edge })"
        @click="$emit('edgeClick', { event: $event, edge: edge })"
    />
</g>
`
};


const perObjectFn = {
    type: Function,
    validator: (fn) => fn.length === 1
};

/**
 * Vue component that renders a directed SMARTS graph as an interactive SVG.
 */
const SmartsGraph = {
    name: 'SmartsGraph',
    emits: ['edgeClick', 'nodeClick', 'edgeHover', 'nodeHover', 'backgroundClick'],
    components: {
        ArrowheadMarkers, SmartsNodes, SmartsSubsetEdges
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
        nodeClassFn:   { ...perObjectFn, default: (_node) => {} },
        /** A function that returns a color given a node (white by default). */
        nodeColorFn:   { ...perObjectFn, default: (_node) => 'white' },
        /**
         * A function that returns a (key)->(value) CSS style mapping given a node.
         * No styles by default
         */
        nodeStyleFn:   { ...perObjectFn, default: (_node) => {} },
        /**
         * A function that determines if a node is active
         * (shown, included in the layout and force simulation, visited during DFS)
         */
        nodeActiveFn:  { ...perObjectFn, default: (_node) => true },

        /**
         * A function that returns a (CSS class) -> (boolean) mapping given an edge.
         * Only if the boolean is true, the class will be added to the edge.
         * No classes by default.
         */
        edgeClassFn:   { ...perObjectFn, default: (_node) => {} },
        /** A function that returns a color given a node (black by default). */
        edgeColorFn:   {
            ...perObjectFn,
            default: (_edge) => 'black',
            validator: (fn) => fn.length === 1 && fn.colors instanceof Array,
        },
        /**
         * A function that returns a (key)->(value) CSS style mapping given an edge.
         * No styles by default
         */
        edgeStyleFn:   { ...perObjectFn, default: (_edge) => {} },
        /**
         * A function that determines if an edge is active
         * (shown, included in the layout and force simulation, traversed during DFS)
         */
        edgeActiveFn:  { ...perObjectFn, default: (_edge) => true },
    },
    data() {
        return {
            isObjectSelectionFixed: false
        };
    },
    template: `
<svg ref="graphSvg" width="100%" height="100%" @click.self="handleBackgroundClick">
    <defs>
        <arrowhead-markers :colors="edgeColorFn.colors" />
        <slot></slot>
    </defs>
    <g ref="graphSvgMasterGroup" @click.self="handleBackgroundClick">
        <smarts-subset-edges :edges="activeEdges"
            :classFn="edgeClassFn"
            :colorFn="edgeColorFn"
            :styleFn="edgeStyleFn"
            @edgeClick="$emit('edgeClick', $event)"
            @edgeHover="$emit('edgeHover', $event)"
            @click.self="handleBackgroundClick"
        />
        <smarts-nodes :nodes="activeNodes"
            :classFn="nodeClassFn_"
            :colorFn="nodeColorFn"
            :styleFn="nodeStyleFn"
            @nodeClick="$emit('nodeClick', $event)"
            @nodeHover="$emit('nodeHover', $event)"
            @nodeDblClick="handleNodeDblClick($event)"
            @nodeDrag="handleNodeDrag($event)"
            @nodeDragStart="handleNodeDragStart($event)"
            @nodeDragEnd="handleNodeDragEnd($event)"
            @click.self="handleBackgroundClick"
        />
    </g>
</svg>
`,
    /** Computed props of this component */
    computed: {
        /**
         * The currently active edges (determined by the edgeActiveFn prop)
         */
        activeEdges() {
            return _.filter(this.graph.edges, this.edgeActiveFn);
        },
        /**
         * The currently active nodes (determined by the nodeActiveFn prop)
         */
        activeNodes() {
            return _.filter(this.graph.nodes, this.nodeActiveFn);
        },
        /**
         * Merges external nodeClassFn behavior with component-internal behavior
         */
        nodeClassFn_() {
            return (node) => {
                return { ...this.nodeClassFn(node), 'node-fixed': node.__dragFixed }
            };
        }
    },
    /**
     * Sets up a watcher to reinitialize the graph simulation if the graph or the active edges
     * change (not deep-watching, so only triggers when these are replaced)
     */
    beforeMount() {
        this.$watch(() => [this.graph, this.activeEdges], (_newVal) => {
            this.initGraphSimulation();
        }, { immediate: true });
    },
    /**
     * Sets up the zoom functionality for the graph
     */
    mounted() {
        this.initGraphZoom();
    },
    /**
     * The methods of this component
     */
    methods: {
        /**
         * Initialize the graph simulation and return the SimulatedGraph instance
         */
        initGraphSimulation() {
            this.initSimulation();
            this._simulatedGraph = new SimulatedGraph(
                this.graph, this._simulation, this.edgeActiveFn, this.nodeActiveFn
            );
            return this._simulatedGraph;
        },
        /**
         * Set up and store a simulation with the devised forces and parameters.
         */
        initSimulation() {
            if(this._simulation) { this._simulation.stop(); }

            this._simulation = d3.forceSimulation()
                .force('charge', d3.forceManyBody()
                    .strength(node => {
                        return -30 * Math.log(1 + node.incidentEdges.length);
                    }))
                .force('link', d3.forceLink()
                    .id(edge => edge.id)
                    .distance(edge => edge.type === 'equal' ? 75 : 150)
                    .strength(1)
                    .iterations(3))
                .force('collision', d3.forceCollide()
                    .radius(22.5))
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
            const root = d3.select(this.$refs.graphSvg);
            // update node positions
            root.selectAll('circle.node').data(this._simulatedGraph.simulacrum.nodes, getId)
                .attr('cx', node => node.x)
                .attr('cy', node => node.y);
            // update edge positions (real and hoverhelper edges)
            _.each(['line.subset.real', 'line.subset.hoverhelper'], selector => {
                root.selectAll(selector).data(this._simulatedGraph.simulacrum.edges, getId)
                    .attr('x1', edge => edge.source.x)
                    .attr('x2', edge => edge.target.x)
                    .attr('y1', edge => edge.source.y)
                    .attr('y2', edge => edge.target.y);
            });
        },

        /**
         * Sets up panning & zooming for the graph.
         */
        initGraphZoom() {
            let graphSvgElement = this.$refs.graphSvg;
            let masterGroupElement = d3.select(this.$refs.graphSvgMasterGroup);
            let zoom = d3.zoom().scaleExtent([0.1, 2]);

            const initialScale = 0.25;
            const width = graphSvgElement.clientWidth;
            const height = graphSvgElement.clientHeight;
            d3.select(graphSvgElement)
                .call(zoom
                      .on('zoom', event => masterGroupElement.attr("transform", event.transform)))
                .on('dblclick.zoom', null)
                .call(zoom.scaleTo, initialScale)
                .call(zoom.translateTo, -width/2 * initialScale, -height/2 * initialScale);
        },

        /**
         * Handles the user dragging a node, by removing nodes that are not in the same CC from the
         * force simulation. Improves responsiveness.
         */
        handleNodeDragStart({ node }) {
            const { id } = node;
            const { simulacrum } = this._simulatedGraph;
            const simNode = simulacrum.getNodeById(id);

            // Only include nodes in the same connected component in the simulation while dragging,
            // to improve responsiveness
            let ccNodes = [];
            let ccEdges = [];
            this._simulatedGraph.simulacrum.runDFS(
                simNode, 'all', Infinity,
                (node) => { ccNodes.push(node) },
                (edge) => { ccEdges.push(edge) },
                null,
                this.edgeActiveFn);

            this._prevSimNodes = this._simulation.nodes();
            this._simulation.nodes(ccNodes);
            this._prevSimEdges = this._simulation.force('link').links();
            this._simulation.force('link').links(ccEdges);
        },
        /** Handles the user dragging a node, by taking its dragged position as fixed. */
        handleNodeDrag({ node, event }) {
            const { id } = node;
            const { x, y } = event;
            const { simulacrum } = this._simulatedGraph;
            const simNode = simulacrum.getNodeById(id);

            node.__dragFixed = true;
            simNode.fx = x;
            simNode.fy = y;
            this.restartSimulation(0.05, 0.05);
        },
        /**
         * Handles the user stopping to drag a node, by resetting the choice of nodes currently
         * active in the force simulation
         */
        handleNodeDragEnd(_event) {
            if(this._prevSimNodes) {
                this._simulation.nodes(this._prevSimNodes);
                delete this._prevSimNodes;
            }
            if(this._prevSimEdges) {
                this._simulation.force('link').links(this._prevSimEdges);
                delete this._prevSimEdges;
            }
        },
        /**
         * Handles the user double-clicking a node, by unfixing it
         */
        handleNodeDblClick({ node, _event }) {
            const { id } = node;
            const { simulacrum } = this._simulatedGraph;
            const simNode = simulacrum.getNodeById(id);

            node.__dragFixed = false;
            delete simNode.fx;
            delete simNode.fy;
            this.restartSimulation(0.05, 0.05);
        },
        /** Emits an event when the user clicks on the background. */
        handleBackgroundClick(event) {
            this.$emit('backgroundClick', event);
        }
    },
};


export { SmartsGraph, ArrowheadMarker };
