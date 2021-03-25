/////////////// LIBRARY IMPORTS ////////////////////////////////////////////////

// import all -- see https://lodash.com/per-method-packages
import _ from 'lodash';

 // import all -- unable to take specific feature subset
import * as Vue from 'vue';//'vue/dist/vue.esm-bundler';

import * as d3ScaleChromatic from 'd3-scale-chromatic';
import * as d3Interpolate from 'd3-interpolate';
import * as d3Scale from 'd3-scale';
const d3 = Object.assign({}, d3ScaleChromatic, d3Interpolate, d3Scale);

import * as M from 'materialize-css/dist/js/materialize.min.js';

/////////////// COMPONENT IMPORTS //////////////////////////////////////////////

import { Graph } from './graph.js'
import { SmartsGraph, ArrowheadMarker } from './components/smarts-graph.js';
import { InfoBox } from './components/info.js';
import { RangeSlider } from './components/range-slider.js';
import { NodeFix } from './components/node-fix.js';
import { UploadBox } from './components/upload-box.js';
import { InfoButton, AboutButton } from './components/modals.js';

/////////////// STYLE IMPORTS //////////////////////////////////////////////////

import 'materialize-css/sass/materialize.scss';
import './style.css';

/////////////// HELPER FUNCTIONS ///////////////////////////////////////////////

const kellyColors =
      ['#F2F3F4', '#222222', '#F3C300', '#875692', '#F38400',
       '#A1CAF1', '#BE0032', '#C2B280','#848482', '#008856',
       '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600',
       '#B3446C', '#DCD300', '#882D17', '#8DB600', '#654522',
       '#E25822', '#2B3D26'];

/**
 * Returns all SMARTS libraries referred to by a graph's nodes, sorted alphabetically by name.
  * @param {Graph|Object} graph an object containing nodes that all have a 'library' property
 */
function getLibrariesFromGraph(graph) {
    const { nodes } = graph;
    return _.sortBy(_.uniq(_.map(nodes, 'library')));
}

/**
 * Returns an object that maps SMARTS libraries to colors, by order in the libraries array parameter
 * (using the Kelly colors by default).
 * @param {Array} libraries The libraries to map colors for
 * @param {Array} colors (optional) The colors to map to. Kelly colors, if not given.
 * @returns An object mapping libraries (strings) to colors (strings).
 */
function librariesToColorMapping(libraries, colors = kellyColors) {
    return _.chain(libraries)
        .map((name, i) => [name, colors[i]])
        .fromPairs()
        .value();
}

/**
 * Verifies if a SMARTS node matches a search regexp. A falsy (empty/null) regex will lead to a
 * truthy result.
 * @param {Node} node A node object (generally, an object with a name property).
 * @param {Regexp} regexp A Regexp to match against the node's name.
 * @returns true if the regex matches or if the regex is falsy (empty/null). false otherwise.
 */
function matchesSearchRegexp(node, regexp) {
    return !regexp || regexp.test(node.name);
}

/////////////// DEFINE THE APP DESCRIPTION /////////////////////////////////////

/**
 * The main component of the SMARTSexplore app.
 */
const appDescription = {
    name: 'SMARTSexplore',
    components: { SmartsGraph, InfoBox, ArrowheadMarker },
    template: `
<div class="smartsexplore-app" :class="{ 'night-mode': settings.nightMode }">
    <smarts-graph
        ref="graph"
        :graph="graph"
        :nodeColorFn="nodeColorFn"
        :nodeClassFn="nodeClassFn"
        :nodeActiveFn="nodeActiveFn"
        :edgeColorFn="edgeColorFn"
        :edgeStyleFn="edgeStyleFn"
        :edgeClassFn="edgeClassFn"
        :edgeActiveFn="edgeActiveFn"
        @nodeClick="handleNodeClick"
        @nodeHover="handleNodeHover"
        @edgeClick="handleEdgeClick"
        @edgeHover="handleEdgeHover"
        @backgroundClick="handleGraphBackgroundClick"
    >
        <arrowhead-marker id="arrowhead-highlight" />
    </smarts-graph>
    <settings v-model="settings"
        :libraryToColor="libraryToColor"
        :colorMap="similarityToColor"
        :matchesLoaded="matchesLoaded"
        @fileUploadResponse="handleFileUploadResponse"
    />
    <info-box
        :obj="selectedObject"
        :showMatches="matchesLoaded"
    />
</div>
    `,
    /**
     * Generates initial data for the SMARTSexplore app.
     */
    data() {
        return {
            /** The Graph object */
            graph: this.initGraph([], []),
            /** The Regexp object to use for SMARTS searching */
            searchRegexp: null,
            /** The settings object, which is passed to the settings component */
            settings: {
                /** The current library selection, mapping library names to booleans */
                librarySelection: {},
                /** The search string, which is parsed as a Regexp */
                searchString: '',
                /** Denotes if something is wrong with the search string the user put in */
                _searchStringError: false,
                /** Contains information about how to display edge similarity */
                edgeSimilarity: {
                    /**
                     * The colormap to use -- the string should correspond to a property available
                     * on the d3 object as 'interpolate'+colormap, e.g. 'Viridis' is fine,
                     * since 'interpolateViridis' exists
                     */
                    colormap: 'Viridis',
                    /** The number of steps to discretize the colormap with */
                    steps: 5,
                    /**
                     * The similarity range to use for filtering, and to normalize the colormap to
                     */
                    range: [0.65, 1.0]
                },
                /**
                 * Lets the user toggle whether they want the SMARTS nodes to be colored by
                 * molecule matches, or by libraries (default). Only makes sense to be set to true
                 * when matchesLoaded is true as well, i.e., there are match result to render.
                 */
                showMatches: false,
                /** Sets the maximum DFS depth, 1 by default. */
                maxDFSDepth: 1,
                /** Sets the selection mode (hover or click), hover by default. */
                selectOn: 'hover',
                /** Enables/disables night mode. Disabled (false) by default. */
                nightMode: false,
            },
            /**
             * The currently user-selected object (node or edge), which will be displayed
             * in the info box.
             */
            selectedObject: null,
            /** True if there is molecule match data available and loaded. */
            matchesLoaded: false,
            /**
             * Tracks the maximum number of molecule matches any single SMARTS achieved in the
             * last available match data.
             */
            maxMatches: null,
        };
    },
    /** Computed properties of the SMARTSexplore app. */
    computed: {
        /**
         * Whether to display molecule matches, based on ``matchesLoaded``
         * and ``settings.showMatches``.
         * @returns {boolean}
         */
        displayMatches() {
            return this.matchesLoaded && this.settings.showMatches;
        },
        /**
         * The current coloration function for the SMARTS nodes.
         * Switched based on ``displayMatches``:
         *
         * - If displayMatches is true, uses the number of matches relative to the maximum number
         *   of matches of all SMARTS to color each SMARTS node.
         * - If displayMatches is false, uses the mapping of libraries to colors to color each
         *   SMARTS node.
         */
        nodeColorFn() {
            if(this.displayMatches) {
                const colorScale = d3.interpolateYlOrRd;

                return (node) => {
                    const count = node.meta.matches.length;
                    if(!count || !this.maxMatches) {
                        return this.settings.nightMode ? '#333' : 'white';
                    }
                    else return colorScale(0.1 + 0.9 * (Math.log(count)/Math.log(this.maxMatches)));
                };
            }
            else {
                return (node) => this.libraryToColor[node.library];
            }
        },
        /**
         * The current visibility functions for the SMARTS nodes.
         * Nodes are visible if they are included in the library selection and the search regexp
         * matches their name (or is empty).
         */
        nodeVisibleFn_() {
            return (node) => this.settings.librarySelection[node.library]
                && matchesSearchRegexp(node, this.searchRegexp);
        },
        /**
         * The current CSS class function for the SMARTS nodes.
         * Sets 'hidden' if the node is not visible, 'muted' if it has been muted (by DFS actions),
         * 'highlighted' if it is highlighted (by selection via hovering/clicking),
         * and 'transparent-border' if molecule matches are displayed and this node has none.
         */
        nodeClassFn() {
            return (node) => {
                return {
                    'hidden': !this.nodeVisibleFn_(node),
                    'muted': node.meta.muted,
                    'highlighted': node.meta.highlighted,
                    'transparent-border': this.displayMatches && !node.meta.matches.length
                };
            }
        },
        /**
         * The function determining if nodes are active (included in the simulation, DFS, ...).
         * Currently returns the exact same value as nodeVisibleFn.
         */
        nodeActiveFn() {
            return this.nodeVisibleFn_;
        },
        /**
         * The edge coloration function. Uses the current similarity->color mapping,
         * see the similarityToColor computed prop.
         */
        edgeColorFn() {
            return this.similarityToColor;
        },
        /**
         * The edge CSS style function. Determines the numerical edge width based on the similarity
         * value, using a quadratically proportional formula with upper and lower width bounds.
         * Equal edges are all displayed with the maximum thickness.
         */
        edgeStyleFn() {
            const scale = d3.scaleLinear()
                .domain(this.settings.edgeSimilarity.range).range([0, 1]);
            return (edge) => {
                const strokeWidth = (
                    edge.type === 'equal'
                    ? 10
                    : Math.min(Math.max(2.5, 8 * scale(edge.spsim)**2), 10)
                );
                return { strokeWidth };
            };
        },
        /**
         * The edge CSS class function. Mostly combines results for the nodes this edge connects.
         * If at least one node is hidden or muted, the edge is, too.
         * Apart from this, sets 'highlighted' if the edge is selected, and 'equal' if it is an
         * equal edge.
         */
        edgeClassFn() {
            const nodeVisibleFn = this.nodeVisibleFn_;
            return (edge) => {
                const { source, target } = edge;
                const muted = (source.meta.muted || target.meta.muted) || (
                    this.displayMatches && !(source.meta.matches.length && target.meta.matches.length)
                );

                return {
                    'hidden': !nodeVisibleFn(source) || !nodeVisibleFn(target),
                    'muted': muted,
                    'highlighted': edge.meta.highlighted,
                    'equal': edge.type === 'equal'
                };
            }
        },
        /**
         * The function determining if an edge is active (included in the simulation, DFS, ...).
         * For the edge to be active, both connected nodes must be visible, and the edge must fall
         * within the chosen edge similarity range.
         */
        edgeActiveFn() {
            const nodeVisibleFn = this.nodeVisibleFn_;
            return (edge) => {
                const { source, target } = edge;
                const [min, max] = this.settings.edgeSimilarity.range;
                return nodeVisibleFn(source) && nodeVisibleFn(target) &&
                    min <= edge.spsim && edge.spsim <= max;
            }
        },
        /**
         * All SMARTS libraries stored in the graph, see ``getLibrariesFromGraph``.
         */
        graphLibraries() {
            return getLibrariesFromGraph(this.graph);
        },
        /**
         * Maps libraries to colors, see ``librariesToColorMapping``.
         */
        libraryToColor() {
            return librariesToColorMapping(this.graphLibraries);
        },
        /**
         * Maps edge similarity to a color value, based on the edgeSimilarity settings.
         * Configured by the number of quantization steps, the chosen color map
         * (all from d3-scale-chromatic are available), and the currently chosen similarity range
         * (for normalization).
         */
        similarityToColor() {
            const { steps, colormap, range } = this.settings.edgeSimilarity;
            let key = `interpolate${colormap}`;
            if(!colormap || !(key in d3)) key = 'interpolateViridis';

            const colors = d3.quantize(d3[key], steps || 2);
            const colorScale = d3.scaleQuantize().domain(range).range(colors);

            const colorFn = (edge) => {
                if(edge.type === 'equal') return this.settings.nightMode ? '#ffffff' : '#000000';
                else return colorScale(edge.spsim);
            }
            colorFn.colors = colors;
            return colorFn;
        },
    },
    methods: {
        /**
         * Initializes and returns a new Graph given nodes and edges, equipping the graph with
         * the required default meta information for nodes and for edges.
         */
        initGraph(nodes, edges) {
            const nodeMeta = { muted: false, highlighted: false, matches: [] };
            const edgeMeta = { highlighted: false };
            return new Graph(nodes, edges, nodeMeta, edgeMeta, true);
        },
        /**
         * Fetches the (initial) graph from the backend and replaces this.graph with it.
         * Shows a Materialize toast if anything goes wrong.
         */
        async fetchGraph() {
            const request = fetch('/smarts/data', {
                method: 'post',
                body: JSON.stringify({ 'spsim_min': 0, 'spsim_max': 1 }),
                headers: { 'Content-Type': 'application/json' }
            });

            try {
                const response = await request;
                const json = await response.json();
                const ok = response.ok;

                if(ok) {
                    const graph = this.initGraph(json.nodes, json.edges);
                    this.graph = graph;
                }
                else {
                    throw new Error(json.error || String(response.status));
                }
            } catch(e) {
                console.error(e);
                M.toast({
                    html: `
                        Could not fetch graph data. Please retry later or contact an administrator.
                        Error: ${e}
                    `,
                    displayLength: Math.inf
                });
            }
        },
        /**
         * Handles users hovering over an edge: if selectOn == 'hover', sets the selected object
         * to be the hovered edge.
         */
        handleEdgeHover({ edge, event }) {
            if(this.settings.selectOn == 'hover'){
                this.selectedObject = edge;
            }
        },
        /**
         * Handles users clicking an edge: if selectOn == 'click', sets the selected object
         * to be the clicked edge.
         */
        handleEdgeClick({ edge, event }) {
            if(this.settings.selectOn == 'click'){
                this.selectedObject = edge;
            }
        },
        /**
         * Handles users hovering over a node:
         *
         *   * if selectOn == 'hover', sets the selected object to be the hovered node.
         *   * if alt (incoming) or shift (outgoing) are held while hovering, runs a DFS in the
         *     given direction and mutes all unreached nodes.
         *   * if both alt and shift are held, runs an undirected DFS and mutes all unreached nodes.
         */
        handleNodeHover({ node, event }) {
            if(event.altKey || event.shiftKey) {
                const maxDepth = this.settings.maxDFSDepth;
                let dir = 'all';
                if(event.shiftKey && !event.altKey) dir = 'outgoing';
                else if(event.altKey && !event.shiftKey) dir = 'incoming';

                // Mute all nodes, unmute only reached nodes
                _.each(this.graph.nodes, (node) => { node.meta.muted = true; })
                this.graph.runDFS(
                    node, dir, maxDepth,
                    (node) => { node.meta.muted = false; },
                    null, null, this.edgeActiveFn, null
                );
            }

            if(this.settings.selectOn  == 'hover'){
                this.selectedObject = node;
            }
        },
        /**
         * Handles users clicking a node: if selectOn == 'click', sets the selected object
         * to be the clicked node.
         */
        handleNodeClick({ node, event }) {
            if(this.settings.selectOn == 'click') {
                this.selectedObject = node;
            }
        },
        /**
         * Handles users clicking the background: If shift or alt are held, unmutes all nodes
         * (reverting the effects of alt/shift node hover).
         */
        handleGraphBackgroundClick(event) {
            if(event.altKey || event.shiftKey) {
                // unmute all nodes
                _.each(this.graph.nodes, (node) => { node.meta.muted = false; })
            }
        },
        /**
         * Handles a (successful) response of the backend to a molecule upload request.
         * Stores match data and sets the application up to show it.
         */
        handleFileUploadResponse(response) {
            const { matches } = response;
            const matchesPerSMARTS = {};

            _.each(this.graph.nodes, (node) => {
                node.meta.matches.length = 0;  // prune existing data
            });
            _.each(matches, (match) => {
                const node = this.graph.getNodeById(match.smarts_id);
                const prevMatches = matchesPerSMARTS[match.smarts_id];
                matchesPerSMARTS[match.smarts_id] = prevMatches ? prevMatches + 1 : 1;
                node.meta.matches.push(match);
            });
            _.each(this.graph.nodes, (node) => {
                node.meta.matches = _.sortBy(node.meta.matches, 'molecule_id');
            });

            this.maxMatches = _.max(Object.values(matchesPerSMARTS));
            this.matchesLoaded = true;
            this.settings.showMatches = true;  // user probably will want to see results right away
        }
    },
    /**
     * Watchers of the SMARTSexplore app
     */
    watch: {
        /**
         * Watches 'selectedObject' and updates the 'highlighted' meta attribute on both the
         * previously selected and the newly selected object.
         */
        selectedObject(newVal, oldVal) {
            // this is a Vue-specific optimization: We could check for each object if it is
            // highlighted by comparing against this.selectedObject, but this will add a render
            // update dependency on this.selectedObject for *every such object*, i.e., changing
            // this.selectedObject would trigger an update on *every edge and node*.
            //
            // Instead, we keep the update dependency one-sided by watching selectedObject and
            // only applying a change on the old & new selectedObject's meta information.
            if(newVal) newVal.meta.highlighted = true;
            if(oldVal && oldVal !== newVal) oldVal.meta.highlighted = false;
        },
        /**
         * Watches 'graphLibraries' and keeps the library selection up to date, by dropping removed
         * libraries and adding new libraries with a default 'true' value for the selection
         */
        graphLibraries(newVal, oldVal) {
            // If the list of graph libraries changes, update the library selection accordingly:
            const sel = this.settings.librarySelection;
            //  - if new libraries were added, set their selection to 'true'
            _.each(newVal, (library) => {
                sel[library] = library in sel ? sel[library] : true;
            });
            //  - if libraries were removed, remove them from the selection dict
            _.each(Object.keys(sel), (library) => {
                if(_.indexOf(newVal, library) === -1) {
                    delete sel[library];
                }
            });
        },
        /**
         * Watches 'searchString' to parse it as a regular expression, updates 'searchRegexp' if
         * parsing is successful, and sets an error flag if parsing fails.
         */
        'settings.searchString': function(newVal, oldVal) {
            try {
                const regexp = new RegExp(newVal, 'i');
                this.settings._searchStringError = false;
                this.searchRegexp = regexp;
            } catch(e) {
                this.settings._searchStringError = true;
            }
        }
    },
    /**
     * Before mounting this component, starts to fetch the initial graph from the backend.
     */
    beforeMount() {
        this.fetchGraph();
    }
};

////////////////////// DEFINE THE APP AND ITS COMPONENTS ///////////////////////

const app = Vue.createApp(appDescription);

////////// SETTINGS CONTAINER //////////

app.component('collapsible', {
    // TODO
});

app.component('settings', {
    name: 'settings',
    components: { RangeSlider, NodeFix, UploadBox, InfoButton, AboutButton },
    emits: ['update:modelValue', 'fileUploadResponse'],
    props: {
        modelValue: Object,
        libraryToColor: Object,
        colorMap: {
            type: Function,
            validator: (fn) => fn.length == 1 && fn.colors instanceof Array
        },
        matchesLoaded: Boolean
    },
    data() {
        return {
            moleculeSetUploadUrl: '/molecules/upload'
        };
    },
    computed: {
        s: {
            get() {
                return this.modelValue;
            },
            set(value) {
                this.$emit('update:modelValue', value);
            }
        },
        colorbarBlockWidth() {
            return (1 / this.colorMap.colors.length) * 100 + '%';
        },
        libraryIDs() {
            let result = _.sortBy(Object.keys(this.s.librarySelection));
            return result;
        }
    },
    mounted() {
        this._collapsible = M.Collapsible.init(this.$refs.collapsible, {
            accordion: false,
        });
    },
    beforeUnmount() {
        this._collapsible.destroy();
    },
    methods: {
        selectAllLibraries() {
            Object.keys(this.s.librarySelection).forEach((k) => {
                this.s.librarySelection[k] = true;
            });
        },
        deselectAllLibraries() {
            Object.keys(this.s.librarySelection).forEach((k) => {
                this.s.librarySelection[k] = false;
            });
        },
    },
    template: `
<div class="settings-container">
    <ul ref="collapsible" class="collapsible">
        <li class="active">
            <div class="collapsible-header">
                <i class="material-icons">info_outline</i>Info
            </div>
            <div class="collapsible-body">
                <div class="row info">
                    <label>SMARTSexplore is a network analysis tool [...]</label>
                    <div class="row info button">
                        <about-button/>
                    </div>
                </div>
            </div>
        </li>
        <li class="active">
            <div class="collapsible-header">
                <i class="material-icons">my_location</i>Focus
            </div>
            <div class="collapsible-body">
                <div class="row focus">
                    <div class="object-selection col s12">
                        <nodeFix v-model="s.selectOn"/>
                    </div>
                </div>
                <div class="row dfs-settings">
                    <div class="col s6">
                        <label>
                            DFS depth
                            <input type="number" v-model.number="s.maxDFSDepth" min="1" max="10" step="1" />
                        </label>
                    </div>
                    <div class="col s6">
                        <div><label>Night mode</label></div>
                        <label class="input-like">
                            <input type="checkbox" v-model.bool="s.nightMode" />
                            <span>{{ s.nightMode ? 'En' : 'Dis' }}abled</span>
                        </label>
                    </div>
                </div>
            </div>
        </li>
        <li class="active">
            <div class="collapsible-header">
                <i class="material-icons">adjust</i>Node selection
            </div>
            <div class="collapsible-body">
                <div class="row search">
                    <div class="search-container input-field col s12">
                        <i class="material-icons prefix">search</i>
                        <input id="searchbar" :class="{'invalid': s._searchStringError}"
                            v-model.lazy="s.searchString" type="text" />
                        <label for="searchbar">Search nodes by name</label>
                    </div>
                </div>

                <div class="row library-select">
                    <div class="col s12">
                        <label>
                            Library selection:
                            <a href="#" @click="selectAllLibraries">All</a> |
                            <a href="#" @click="deselectAllLibraries">None</a>
                        </label>

                        <div class="row">
                            <!-- FIXME horribly hacky, but what else should we do with this MaterializeCSS selector? -->
                            <div class="col s12 l6 library-selector" v-for="libraryID in libraryIDs">
                                <component is="style">
                                    [type=checkbox]#__library-checkbox-{{ libraryID }}:checked + span::after {
                                        background-color: {{ libraryToColor[libraryID] }};
                                        border-color: transparent;
                                    }
                                </component>
                                <label>
                                    <input type="checkbox" class="filled-in" v-model="s.librarySelection[libraryID]"
                                        :id="'__library-checkbox-' + libraryID" />
                                    <span>{{ libraryID }}</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row info-button">
                    <div class="col s12">
                      <info-button/>
                    </div>
                </div>
            </div>
        </li>
        <li class="active">
            <div class="collapsible-header">
                <i class="material-icons">trending_flat</i>Edge selection
            </div>
            <div class="collapsible-body">
                <div class="row">
                    <div class="col s12">
                        <rangeSlider :min="0" :max="1" :step="0.01"
                                    :startMin="s.edgeSimilarity.range[0]" :startMax="s.edgeSimilarity.range[1]"
                                    v-model="s.edgeSimilarity.range" />
                    </div>
                </div>
                <div class="row">
                    <div class="col s8">
                        <label class="display-block">Colorscale of current range</label>
                        <div class="colorbar">
                            <span class="colorbar-block" v-for="color in colorMap.colors"
                                :style="{ background: color, width: colorbarBlockWidth }">
                            </span>
                        </div>
                    </div>
                    <div class="col s4">
                        <label>
                            Steps
                            <input type="number" v-model.number="s.edgeSimilarity.steps" min="2" max="10"
                                step="1" />
                        </label>
                    </div>
                </div>
            </div>
        </li>
        <li class="active">
            <div class="collapsible-header">
                <i class="material-icons">file_upload</i>Molecule Upload
            </div>
            <div class="collapsible-body">
                <div class="row upload-box">
                    <div class="col s12">
                        <upload-box :target-url="moleculeSetUploadUrl" @response="$emit('fileUploadResponse', $event)" />
                    </div>
                    <div class="col s12 matches-toggle" v-if="matchesLoaded">
                        <label>
                            <input v-model="s.showMatches" type="checkbox" class="filled-in">
                            <span>Show molecule matches</span>
                        </label>
                    </div>
                </div>
            </div>
        </li>
    </ul>
</div>
`,
});


export { app };
