<template>
<div class='info-container'>
    <div class='title' v-html='title'></div>
    <div class='smarts-preview' ref='previewWrapper'>
        <div>
            <svg ref='previewSvg'>
                <g ref='previewSvgGroup'>
                  <image :href='previewHref' alt='1' @error='handleImageError'/>
                </g>
            </svg>
        </div>
    </div>
    <smarts-info v-if='objType === "node"' :smarts='obj' :showMatches='showMatches' />
    <smarts-subset-edge-info v-if='objType === "edge"' :edge='obj' :showMatches='showMatches' />
</div>

</template>

<script>
/* eslint max-len: */

/**
 * Vue component that renders the information box of SMARTSexplore,
 * displaying an appropriate image and otherwise wrapping the SmartsInfo and SmartsSubsetEdgeInfo
 * components (depending on whether it's showing a SMARTS node or a subset edge).
 */

import {Node, Edge} from './graphComponents/graph.js';
import SmartsInfo from './ImageBoxComponents/SmartsInfo.vue';
import SmartsSubsetEdgeInfo from './ImageBoxComponents/SmartsSubsetEdgeInfo.vue';

import * as d3 from 'd3';

export default {
  name: 'ImageBox',
  components: {SmartsInfo, SmartsSubsetEdgeInfo},
  emits: ['previewZoomStart', 'previewZoomEnd'],
  props: {
    obj: Object,
    showMatches: Boolean,
  },
  /** Computed props of this component */
  computed: {
    /**
     * The tupe of the rendered object (as a string). Possible return values are
     * 'node', 'edge' and 'null'.
     * @return {obj}
     */
    objType: function() {
      const {obj} = this;
      return obj instanceof Node ? 'node' :
          (obj instanceof Edge ? 'edge' : 'null');
    },
    /**
     * The title of the info box. For SMARTS, shows their name. For edges, shows the subset
     * (or equality) relationships by connecting both SMARTS' names with an appropriate symbol.
     *
     * When no object is displayed, shows an instructional string.
     * @return {String}
     */
    title: function() {
      const {obj} = this;
      if (obj === null) {
        return 'Hover over a node or edge to get more info.';
      } else if (obj instanceof Node) {
        return obj.name;
      } else if (obj instanceof Edge) {
        const symbol = (obj.type === 'equal' ? '=' : '⊂');
        return `${obj.source.name} <br> ${symbol} <br> ${obj.target.name}`;
      } else return 'unknown object';
    },
    objId: function() {
      const {obj} = this;
      if (obj instanceof Node) {
        return obj.id;
      } else if (obj instanceof Edge) {
        return obj.id;
      } else return 0;
    },
    /**
     * Determines the href (URL) of the preview image to show.
     * @return {imageURL}
     */
    previewHref: function() {
      const {obj} = this;
      if (obj instanceof Node) {
        return `http://localhost:5000/smarts/smartsview/${obj.id}`;
      } else if (obj instanceof Edge) {
        return `http://localhost:5000/smarts/smartssubsets/${obj.id}`;
      } else {
        console.log('not known type');
        return null; // 'not known type';
      }
    },
  },
  mounted() {
    this.initPreviewZoom();
    this.$watch(
        () => this.obj,
        () => this.resetPreviewZoom(),
        {flush: 'post', deep: false},
    );
  },
  unmounted() {
    this.cleanupPreviewZoom();
  },
  methods: {
    /**
     * Handles errors in image loading by replacing errored image with a static 'missing image'
     * text image.
     * @param {event} event
     */
    handleImageError(event) {
      event.target.setAttribute('src', require('../assets/static/missing-image.svg'));
    },
    /**
     * Initializes and stores the d3-zoom object that controls the displayed
     * SMARTS/subset image ('preview').
     */
    initPreviewZoom() {
      const zoom = d3.zoom().scaleExtent([1, 5]);

      const wrapperElement = this.$refs.previewWrapper;
      const selector = d3.select(this.$refs.previewSvg);
      // const masterGroupSelector = d3.select(this.$refs.previewSvgGroup);
      // Define a method to keep the translateExtent property up to date
      /**
       * Translate the preview
       */
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
      // console.log(masterGroupSelector)
      // zoom.on('zoom', event => masterGroupSelector.attr('transform', event.transform));
      selector
          .call(zoom)
          .on('dblclick.zoom', null)
          .on('start', () => this.$emit('previewZoomStart')) // TODO document these events
          .on('end', () => this.$emit('previewZoomEnd')); // TODO also have them have the effect of locking the update

      this.previewZoom = {zoom, selector};
    },
    /**
     * Resets the transform of the preview zoom to identity (no transformation).
     */
    resetPreviewZoom() {
      if (this.previewZoom) {
        this.previewZoom.selector.call(this.previewZoom.zoom.transform, d3.zoomIdentity);
      }
    },
    /**
     * Cleans up the preview zoom (for unmounting)
     */
    cleanupPreviewZoom() {
      this._windowSelector.on('resize', null);
      this.previewZoom.zoom.on('zoom', null);
    },
  },
};
</script>


<style>
.info-container {
    top: .5rem;
    right: .5rem;
    width: 20vw;
    padding: 1rem;
}
.info-container .title {
    font-size: 1.2rem;
    overflow-wrap: break-word;
    font-variant: small-caps;
}

/* SMARTS preview */

.smarts-preview {
    margin: 0;
    padding: 0;
}
.smarts-preview {
    width: 100%;
    padding-top: 100%;
    position: relative;
    margin: 1rem 0;
    border-radius: 2px;
}
.smarts-preview > div {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
}
.smarts-preview svg {
    width: 100%;
    height: 100%;
}
.smarts-preview image {
    width: 100%;
    height: auto;
}

</style>
