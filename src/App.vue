<template>
<div class="smartsexplore-app" :class="{ 'night-mode': settings.nightMode }">
  <SmartsGraph v-if="currentGraph=='SmartsGraph'"
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
   />
   <!-- :displayMatches="displayMatches" -->
   <d3Canvas v-if="currentGraph=='d3Canvas'"
      :graph="graph"
      :displayMatches="displayMatches"
      :steps="settings.edgeSimilarity.steps"
      :detph="settings.maxDFSDepth"
      :modus="settings.selectOn"
      :nodeColorFn="nodeColorFn"
      :nodeClassFn="nodeClassFn"
      :nodeActiveFn="nodeActiveFn"
      :edgeColorFn="edgeColorFn"
      :edgeStyleFn="edgeStyleFn"
      :edgeClassFn="edgeClassFn"
      :edgeActiveFn="edgeActiveFn"
      @nodeHover="handleNodeHover"
      @edgeHover="handleEdgeHover"
      @nodeClick="handleNodeClick"
      @edgeClick="handleEdgeClick"
      @backgroundClick="handleGraphBackgroundClick"
    />
    <d3Layout v-if="currentGraph=='d3Lyaout'"
    />
    <d3Svg v-if="currentGraph=='d3Svg'"
      :graph="graph"
      :nodeColorFn="nodeColorFn"
      :nodeClassFn="nodeClassFn"
      :nodeActiveFn="nodeActiveFn"
      :edgeColorFn="edgeColorFn"
      :edgeStyleFn="edgeStyleFn"
      :edgeClassFn="edgeClassFn"
      :edgeActiveFn="edgeActiveFn"
      @nodeHover="handleNodeHover"
      @edgeHover="handleEdgeHover"
      @nodeClick="handleNodeClick"
      @edgeClick="handleEdgeClick"
    />
  <settings
    v-model="settings"
    :libraryToColor="libraryToColor"
    :colorMap="similarityToColor"
    :matchesLoaded="matchesLoaded"
    @fileUploadResponse="handleFileUploadResponse"
  />
  <ImageBox
    :obj="selectedObject"
    :showMatches="matchesLoaded"
  />
</div>

</template>

<script>
/* eslint max-len: */
import Settings from './components/Settings.vue';
import ImageBox from './components/ImageBox.vue';
import d3Layout from './components/graphCollection/d3Layout.vue';
import d3Canvas from './components/graphCollection/d3Canvas.vue';
import d3Svg from './components/graphCollection/d3Svg.vue';

import SmartsGraph from './components/graphCollection/SmartsGraph.vue';
import {Graph} from './components/graphComponents/graph.js';

import * as d3ScaleChromatic from 'd3-scale-chromatic';
import * as d3Interpolate from 'd3-interpolate';
import * as d3Scale from 'd3-scale';
import * as d3Or from 'd3';
const d3 = Object.assign({}, d3Or, d3ScaleChromatic, d3Interpolate, d3Scale);

import 'materialize-css/sass/materialize.scss';
import * as M from 'materialize-css/dist/js/materialize.min.js';

export default {
  name: 'App',
  components: {
    Settings,
    ImageBox,
    d3Canvas,
    SmartsGraph,
    d3Layout,
    d3Svg,
  },
  data() {
    return {
      /** select the current implementation fo the graph
       * Smartsgraph: the implementation given
       * d3Layout: old d3 library
       * d3Svg: another implementation with SVG which runs faster than the old one. There are still bugs.
       * d3Canvas: the fastet implementation so far. It uses Canvas instead of SVG
       */
      currentGraph: 'd3Canvas', // SmartsGraph / d3Layout / d3Canvas  / d3Svg
      kellyColors:
        ['#F2F3F4', '#222222', '#F3C300', '#875692', '#F38400',
          '#A1CAF1', '#BE0032', '#C2B280', '#848482', '#008856',
          '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600',
          '#B3446C', '#DCD300', '#882D17', '#8DB600', '#654522',
          '#E25822', '#2B3D26'],
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
        searchStringError: false,
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
          range: [0.65, 1.0],
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
     * @return {boolean}
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
     * @return {color}
     */
    nodeColorFn() {
      if (this.displayMatches) {
        return (node) => {
          const count = node.meta.matches.length;
          if (!count || !this.maxMatches) {
            return this.settings.nightMode ? '#333' : 'white';
          } else {
            return d3.interpolateYlOrRd(0.1 + 0.9 * (Math.log(count)/Math.log(this.maxMatches)));
          }
        };
      } else {
        return (node) => this.libraryToColor[node.library];
      }
    },
    /**
     * The current visibility functions for the SMARTS nodes.
     * Nodes are visible if they are included in the library selection and the search regexp
     * matches their name (or is empty).
     * @return {nodes}
     */
    nodeVisibleFn_() {
      return (node) => this.settings.librarySelection[node.library] &&
      (!this.searchRegexp || this.searchRegexp.test(node.name));
    },
    /**
     * The current CSS class function for the SMARTS nodes.
     * Sets 'hidden' if the node is not visible, 'muted' if it has been muted (by DFS actions),
     * 'highlighted' if it is highlighted (by selection via hovering/clicking),
     * and 'transparent-border' if molecule matches are displayed and this node has none.
     * @return {nodes}
     */
    nodeClassFn() {
      return (node) => {
        return {
          'hidden': !this.nodeVisibleFn_(node),
          'muted': node.meta.muted,
          'highlighted': node.meta.highlighted,
          'transparent-border': this.displayMatches && !node.meta.matches.length,
        };
      };
    },
    /**
     * The function determining if nodes are active (included in the simulation, DFS, ...).
     * Currently returns the exact same value as nodeVisibleFn.
     * @return {nodes}
     */
    nodeActiveFn() {
      return this.nodeVisibleFn_;
    },
    /**
     * The edge coloration function. Uses the current similarity->color mapping,
     * see the similarityToColor computed prop.
     * @return {colors}
     */
    edgeColorFn() {
      return this.similarityToColor;
    },
    /**
     * The edge CSS style function. Determines the numerical edge width based on the similarity
     * value, using a quadratically proportional formula with upper and lower width bounds.
     * Equal edges are all displayed with the maximum thickness.
     * @return {widths}
     */
    edgeStyleFn() {
      const scale = d3.scaleLinear()
          .domain(this.settings.edgeSimilarity.range).range([0, 1]);
      return (edge) => {
        const strokeWidth = (
            edge.type === 'equal' ? 10: Math.min(Math.max(2.5, 8 * scale(edge.spsim)**2), 10)
        );
        return {strokeWidth};
      };
    },
    /**
     * The edge CSS class function. Mostly combines results for the nodes this edge connects.
     * If at least one node is hidden or muted, the edge is, too.
     * Apart from this, sets 'highlighted' if the edge is selected, and 'equal' if it is an
     * equal edge.
     * @return {edges}
     */
    edgeClassFn() {
      const nodeVisibleFn = this.nodeVisibleFn_;
      return (edge) => {
        const {source, target} = edge;
        const muted = (source.meta.muted || target.meta.muted) || (
          this.displayMatches && !(source.meta.matches.length && target.meta.matches.length)
        );

        return {
          'hidden': !nodeVisibleFn(source) || !nodeVisibleFn(target),
          'muted': muted,
          'highlighted': edge.meta.highlighted,
          'equal': edge.type === 'equal',
        };
      };
    },
    /**
     * The function determining if an edge is active (included in the simulation, DFS, ...).
     * For the edge to be active, both connected nodes must be visible, and the edge must fall
     * within the chosen edge similarity range.
     * @return {edges}
     */
    edgeActiveFn() {
      const nodeVisibleFn = this.nodeVisibleFn_;
      return (edge) => {
        const {source, target} = edge;
        const [min, max] = this.settings.edgeSimilarity.range;
        return nodeVisibleFn(source) && nodeVisibleFn(target) &&
            min <= edge.spsim && edge.spsim <= max;
      };
    },
    /**
     * All SMARTS libraries stored in the graph, see ``getLibrariesFromGraph``.
     * @return {libraries}
     */
    graphLibraries() {
      const {nodes} = this.graph;
      const libraries = _.sortBy(_.uniq(_.map(nodes, 'library')));
      return libraries;
    },
    /**
     * Maps libraries to colors, see ``librariesToColorMapping``.
     * @return {colors}
     */
    libraryToColor() {
      return _.chain(this.graphLibraries)
          .map((name, i) => [name, this.kellyColors[i]])
          .fromPairs()
          .value();
    },
    /**
     * Maps edge similarity to a color value, based on the edgeSimilarity settings.
     * Configured by the number of quantization steps, the chosen color map
     * (all from d3-scale-chromatic are available), and the currently chosen similarity range
     * (for normalization).
     * @return {colors}
     */
    similarityToColor() {
      const {steps, colormap, range} = this.settings.edgeSimilarity;
      let key = `interpolate${colormap}`;
      if (!colormap || !(key in d3)) key = 'interpolateViridis';

      const colors = d3.quantize(d3[key], steps || 2);
      const colorScale = d3.scaleQuantize().domain(range).range(colors);

      const colorFn = (edge) => {
        if (edge.type === 'equal') return this.settings.nightMode ? '#ffffff' : '#000000';
        else return colorScale(edge.spsim);
      };
      colorFn.colors = colors;
      return colorFn;
    },
  },
  methods: {
    /**
     * Initializes and returns a new Graph given nodes and edges, equipping the graph with
     * the required default meta information for nodes and for edges.
     * @param {nodes} nodes
     * @param {edges} edges
     * @return {Graph}
     */
    initGraph(nodes, edges) {
      const nodeMeta = {muted: false, highlighted: false, matches: []};
      const edgeMeta = {highlighted: false};
      return new Graph(nodes, edges, nodeMeta, edgeMeta, true);
    },
    /**
     * Fetches the (initial) graph from the backend and replaces this.graph with it.
     * Shows a Materialize toast if anything goes wrong.
     */
    async fetchGraph() {
      const request = fetch('http://localhost:5000/smarts/data', {
        method: 'post',
        body: JSON.stringify({'spsim_min': 0, 'spsim_max': 1}),
        headers: {'Content-Type': 'application/json'},
      });

      try {
        const response = await request;
        const json = await response.json();
        const ok = response.ok;
        if (ok) {
          const graph = this.initGraph(json.nodes, json.edges);
          this.graph = graph;
        } else {
          throw new Error(json.error || String(response.status));
        }
      } catch (e) {
        console.error(e);
        M.toast({
          html: `
              Could not fetch graph data. Please retry later or contact an administrator.
              Error: ${e}
          `,
          displayLength: Math.inf,
        });
      }
    },
    /**
     * Handles users hovering over an edge: if selectOn == 'hover', sets the selected object
     * to be the hovered edge.
     */
    handleEdgeHover({edge, event}) {
      if (this.settings.selectOn == 'hover' ) {
        this.selectedObject = edge;
      }
    },
    /**
     * Handles users clicking an edge: if selectOn == 'click', sets the selected object
     * to be the clicked edge.
     */
    handleEdgeClick({edge, event}) {
      if (this.settings.selectOn == 'click') {
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
    handleNodeHover({node, event}) {
      if (event.altKey || event.shiftKey) {
        const maxDepth = this.settings.maxDFSDepth;
        let dir = 'all';
        if (event.shiftKey && !event.altKey) dir = 'outgoing';
        else if (event.altKey && !event.shiftKey) dir = 'incoming';

        // Mute all nodes, unmute only reached nodes
        _.each(this.graph.nodes, (node) => {
          node.meta.muted = true;
        });
        this.graph.runDFS(
            node, dir, maxDepth,
            (node) => {
              node.meta.muted = false;
            },
            null, null, this.edgeActiveFn, null,
        );
      }

      if (this.settings.selectOn == 'hover') {
        this.selectedObject = node;
      }
    },
    /**
     * Handles users clicking a node: if selectOn == 'click', sets the selected object
     * to be the clicked node.
     * @param {event} event
     */
    handleNodeClick({node, event}) {
      if (this.settings.selectOn == 'click') {
        this.selectedObject = node;
      }
    },
    /**
     * Handles users clicking the background: If shift or alt are held, unmutes all nodes
     * (reverting the effects of alt/shift node hover).
     * @param {event} event
     */
    handleGraphBackgroundClick(event) {
      if (event.altKey || event.shiftKey) {
        // unmute all nodes
        _.each(this.graph.nodes, (node) => {
          node.meta.muted = false;
        });
      }
    },
    /**
     * Handles a (successful) response of the backend to a molecule upload request.
     * Stores match data and sets the application up to show it.
     * @param {response} response
     */
    handleFileUploadResponse(response) {
      const {matches} = response;
      const matchesPerSMARTS = {};

      _.each(this.graph.nodes, (node) => {
        node.meta.matches.length = 0; // prune existing data
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
      this.settings.showMatches = true; // user probably will want to see results right away
    },
  },
  /**
   * Watchers of the SMARTSexplore app
   */
  watch: {
    /**
     * Watches 'selectedObject' and updates the 'highlighted' meta attribute on both the
     * previously selected and the newly selected object.
     * @param {newVal} newVal
     * @param {oldVal} oldVal
     */
    selectedObject(newVal, oldVal) {
      // this is a Vue-specific optimization: We could check for each object if it is
      // highlighted by comparing against this.selectedObject, but this will add a render
      // update dependency on this.selectedObject for *every such object*, i.e., changing
      // this.selectedObject would trigger an update on *every edge and node*.
      //
      // Instead, we keep the update dependency one-sided by watching selectedObject and
      // only applying a change on the old & new selectedObject's meta information.
      if (newVal) newVal.meta.highlighted = true;
      if (oldVal && oldVal !== newVal) oldVal.meta.highlighted = false;
    },
    /**
     * Watches 'graphLibraries' and keeps the library selection up to date, by dropping removed
     * libraries and adding new libraries with a default 'true' value for the selection
     * @param {newVal} newVal
     * @param {oldVal} oldVal
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
        if (_.indexOf(newVal, library) === -1) {
          delete sel[library];
        }
      });
    },
    /**
     * Watches 'searchString' to parse it as a regular expression, updates 'searchRegexp' if
     * parsing is successful, and sets an error flag if parsing fails.
     * @param {newVal} newVal
     * @param {oldVal} oldVal
     */
    'settings.searchString': function(newVal, oldVal) {
      try {
        const regexp = new RegExp(newVal, 'i');
        this.settings.searchStringError = false;
        this.searchRegexp = regexp;
      } catch (e) {
        this.settings.searchStringError = true;
      }
    },
  },
  /**
   * Before mounting this component, starts to fetch the initial graph from the backend.
   */
  beforeMount() {
    this.fetchGraph();
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* Night mode */

.night-mode, .night-mode * {
    color: #eee;
}
.night-mode,
.night-mode .settings-container,
.night-mode .info-container {
    background: #333;
}
.night-mode .collapsible .collapsible-header {
    background: #2a2a2a;
}

.night-mode input:not([type]):disabled,
.night-mode input[type="text"]:not(.browser-default):disabled,
.night-mode input[type="text"]:not(.browser-default)[readonly="readonly"] {
    color: rgba(239, 239, 239, 0.42);
}


html, input, button {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 16px;
}
html, body, .graph-app, .graph-container {
    margin: 0;
    padding: 0;
}

html {
    display: flex;
    flex-direction: column;
    height: 100vh;
}
body {
    overflow: hidden;
}
body, .graph-app {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    height: auto;
}
.smartsexplore-app, .graph-container, .graph-container svg {
    width: 100vw;
    height: 100vh;
}

#toast-container {
    top: auto;
    left: auto;
    bottom: 10%;
    right: 7%;
}

/* Responsive container styling */

@media only screen and (max-width: 600px) {
    .settings-container {
        width: 33.333333333333333333%;
    }
}

@media only screen and (min-width: 601px) and (max-width: 992px) {
    .settings-container {
        width: 33.333333333333333333%;
    }
}

@media only screen and (min-width: 993px) and (max-width: 1200px) {
    .settings-container {
        width: 25%;
    }
}

@media only screen and (min-width: 1201px) {
    .settings-container {
        width: 16.6666666666666666666%;
    }
}

</style>
