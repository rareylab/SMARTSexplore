import _ from 'lodash';

import * as d3Selection from 'd3-selection';
import * as d3Zoom from 'd3-zoom';
const d3 = Object.assign({}, d3Selection, d3Zoom);

import { Copyable, Pluralize } from './util.js';
import { Node, Edge } from '../graph.js';

/**
 * A Vue component that renders a grid of matches, optionally with custom CSS classes attached
 * to each rendered match, based on an arbitrary function's return values.
 */
const MatchesGrid = {
    /**
     * The props of MatchesGrid.
     */
    props: {
        /**
         * An array of matches, which must each be an object containing a ``molecule_name`` (string)
         * and a ``molecule_id`` (integer).
         * @type {array}
         */
        matches: {
            type: Array,
            validator: (val) => _.every(val,
                (match) => 'molecule_name' in match && 'molecule_id' in match
                    && typeof match.molecule_name == 'string'
                    && (match.molecule_id|0) == match.molecule_id
            )
        },
        /**
         * An optional function that associates a CSS class (or multiple, in one space-separated
         * string) with every rendered molecule match.
         * @type {(function(Node): string)}
         */
        classFn: {
            type: Function,
            default: (match) => ''
        }
    },
    template: `
<div class="molecule-grid">
    <span v-for="match in matches"
        :class="'molecule ' + classFn(match)"
        :title="match.molecule_name"
    >
        <label>{{ match.molecule_name }}</label>
        <img :src="getMoleculeImageURL(match.molecule_id)" />
    </span>
</div>
`,
    /**
     * The methods of MatchesGrid.
     */
    methods: {
        /**
         * Gets the appropriate image URL given a molecule id. Doesn't do any validation, neither
         * for existence nor for input data.
         * @param {integer} molecule_id The molecule ID to get an image URL for.
         * @returns {string} The image URL for that molecule.
         */
        getMoleculeImageURL(molecule_id) {
            return `/molecules/images/${molecule_id}`;
        }
    }
};


/**
 * Vue component that displays information about a SMARTS node.
 */
const SmartsInfo = {
    name: 'SmartsInfo',
    components: { Copyable, MatchesGrid, Pluralize },
    props: {
        /** The SMARTS object to display */
        smarts: Object,
        /** Whether to show molecule matches of the SMARTS */
        showMatches: Boolean,
    },
    template: `
<copyable label="Pattern:" :text="smarts.pattern" />

<template v-if="showMatches">
    <label>Molecule matches</label>
    <div class="molecule-matches">
        <span>
            Matching
            <pluralize string="molecule" :count="smarts.meta.matches.length"/>
        </span>
        <matches-grid v-if="smarts.meta.matches.length" :matches="smarts.meta.matches" />
    </div>
</template>
`,
};


/**
 * Vue component that displays information about a directed SMARTS-SMARTS subset edge.
 */
const SmartsSubsetEdgeInfo = {
    name: 'SmartsSubsetEdgeInfo',
    components: { Copyable, MatchesGrid, Pluralize },
    /** Props of this component */
    props: {
        /** The Edge object to display */
        edge: Object,
        /** Whether to show molecule matches on the edge (based on data stored on its SMARTS) */
        showMatches: Boolean,
    },
    template: `
<copyable label="Source pattern:" :text="edge.source.pattern" />
<copyable label="Target pattern:" :text="edge.target.pattern" />
<copyable label="Pattern similarity:" :text="String(edge.spsim)" />

<template v-if="showMatches">
    <label>Molecule matches</label>
    <div class="molecule-matches">
        <span v-if="commonMatches.length">
            <pluralize string="common match" pluralString="common matches"
                :count="commonMatches.length"/>
            (of {{ edge.target.meta.matches.length }})
        </span>
        <span v-else>No common matches</span>

        <matches-grid v-if="commonMatches.length"
            :matches="commonMatches.concat(differentMatches)"
            :classFn="matchClassFn"
        />
    </div>
</template>
`,
    data() {
        return {
            /** Used for highlighting the matches */
            matchClassFn(match) {
                if(match.kind == 'common') { return 'common-match' };
                if(match.kind == 'different') { return 'different-match' }
            }
        }
    },
    /**
     * Computed props of this component
     */
    computed: {
        /**
         * An array of the molecule matches that are *common to* both of this edge's SMARTS.
         * Returns nothing if the showMatches prop is not truthy.
         */
        commonMatches() {
            const { edge, showMatches } = this;
            if(showMatches) {
                return _.map(
                    _.intersectionBy(
                        edge.source.meta.matches, edge.target.meta.matches,
                        'molecule_id'
                    ),
                    (m) => { return { ...m, 'kind': 'common' } }
                )
            }
        },
        /**
         * An array of the molecule matches that are *different between* both of this edge's SMARTS.
         * Returns nothing if the showMatches prop is not truthy.
         */
        differentMatches() {
            const { edge, showMatches } = this;
            if(showMatches) {
                return _.map(
                    _.differenceBy(
                        edge.target.meta.matches, edge.source.meta.matches,
                        'molecule_id'
                    ),
                    (m) => { return { ...m, 'kind': 'different' } }
                )
            }
        }
    }
}

/**
 * Vue component that renders the information box of SMARTSexplore,
 * displaying an appropriate image and otherwise wrapping the SmartsInfo and SmartsSubsetEdgeInfo
 * components (depending on whether it's showing a SMARTS node or a subset edge).
 */
const InfoBox = {
    name: 'InfoBox',
    components: { SmartsInfo, SmartsSubsetEdgeInfo },
    emits: ['previewZoomStart', 'previewZoomEnd'],
    props: {
        obj: Object,
        showMatches: Boolean,
    },
    template: `
<div class="info-container">
    <div class="title" v-html="title"></div>

    <div class="smarts-preview" ref="previewWrapper">
        <div>
            <svg ref="previewSvg">
                <g ref="previewSvgGroup">
                    <image :href="previewHref" @error="handleImageError">
                </image></g>
            </svg>
        </div>
    </div>

    <smarts-info v-if="objType === 'node'" :smarts="obj" :showMatches="showMatches" />
    <smarts-subset-edge-info v-if="objType === 'edge'" :edge="obj" :showMatches="showMatches" />
</div>
`,
    /** Computed props of this component */
    computed: {
        /**
         * The tupe of the rendered object (as a string). Possible return values are
         * 'node', 'edge' and 'null'.
         */
        objType: function() {
            const { obj } = this;
            return obj instanceof Node ? 'node' :
                  (obj instanceof Edge ? 'edge' : 'null');
        },
        /**
         * The title of the info box. For SMARTS, shows their name. For edges, shows the subset
         * (or equality) relationships by connecting both SMARTS' names with an appropriate symbol.
         *
         * When no object is displayed, shows an instructional string.
         */
        title: function() {
            const { obj } = this;
            if(obj === null) {
                return 'Hover over a node or edge to get more info.';
            }
            else if(obj instanceof Node) {
                return obj.name;
            }
            else if(obj instanceof Edge) {
                const symbol = (obj.type === 'equal' ? '=' : '⊂');
                return `${obj.source.name} <br> ${symbol} <br> ${obj.target.name}`;
            }
        },
        /**
         * Determines the href (URL) of the preview image to show.
         */
        previewHref: function() {
            const { obj } = this;
            if(obj instanceof Node) {
                return '/smarts/smartsview/' + obj.id;
            }
            else if(obj instanceof Edge) {
                return '/smarts/smartssubsets/' + obj.id;
            }
        },
    },
    mounted() {
        this.initPreviewZoom();
        this.$watch(
            () => this.obj,
            () => this.resetPreviewZoom(),
            { flush: 'post', deep: false }
        );
    },
    unmounted() {
        this.cleanupPreviewZoom();
    },
    methods: {
        /**
         * Handles errors in image loading by replacing errored image with a static 'missing image'
         * text image.
         */
        handleImageError(event) {
            event.target.setAttribute('href', '/static/missing-image.svg');
        },
        /**
         * Initializes and stores the d3-zoom object that controls the displayed
         * SMARTS/subset image ("preview").
         */
        initPreviewZoom() {
            let zoom = d3.zoom().scaleExtent([1, 5]);

            let wrapperElement = this.$refs.previewWrapper;
            let selector = d3.select(this.$refs.previewSvg);
            let masterGroupSelector = d3.select(this.$refs.previewSvgGroup);
            // Define a method to keep the translateExtent property up to date
            function updatePreviewTranslateExtent() {
                const rect = wrapperElement.getBoundingClientRect();
                const extent = [[0, 0], [rect.width, rect.height]];
                zoom.translateExtent(extent);
            }
            this.$nextTick(updatePreviewTranslateExtent); // call once when DOM is fully ready
            this._windowSelector = d3.select(window);
            this._windowSelector.on('resize', function(event) { // call again on each window resize
                updatePreviewTranslateExtent();
            });

            // Apply the transform to the master group element
            zoom.on('zoom', event => masterGroupSelector.attr("transform", event.transform));
            selector
                .call(zoom)
                .on('dblclick.zoom', null)
                .on('start', () => this.$emit('previewZoomStart'))  // TODO document these events
                .on('end', () => this.$emit('previewZoomEnd'))  // TODO also have them have the effect of locking the update

            this.previewZoom = { zoom, selector };
        },
        /**
         * Resets the transform of the preview zoom to identity (no transformation).
         */
        resetPreviewZoom() {
            if(this.previewZoom) {
                this.previewZoom.selector.call(this.previewZoom.zoom.transform, d3.zoomIdentity);
            }
        },
        /**
         * Cleans up the preview zoom (for unmounting)
         */
        cleanupPreviewZoom() {
            this._windowSelector.on('resize', null);
            this.previewZoom.zoom.on('zoom', null);
        }
    },
};


export { InfoBox, SmartsInfo, SmartsSubsetEdgeInfo };
