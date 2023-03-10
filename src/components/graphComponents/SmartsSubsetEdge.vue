<template>
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
        :data-id="edge.id"/>
</g>
</template>

<script>
/* eslint max-len: */
/**
 * Gets an HTML id from a given color. Only works properly for colors in hex format.
 * Behavior is undefined for other color formats.
 *
 * Used to link up ArrowheadMarkers and SmartsEdges.
 * @param {String} color The color to use.
 * @return {color} The HTML id that can be attached to an element.
 */
function getColorIdFromColor(color) {
  return color.substring(1);
}

export default {
  name: 'SmartsSubsetEdge',
  props: {
    edge: Object,
    classFn: Function,
    colorFn: Function,
    styleFn: Function,
  },
  computed: {
    markerEnd: function() {
      if (this.edge.type === 'equal') return '';
      else {
        const colorId = getColorIdFromColor(this.colorFn(this.edge));
        return `url(#arrowhead-${colorId})`;
      }
    },
  },
};
</script>

<style>
.composite-line:not(:hover):not(.highlighted).muted .edge.real {
    opacity: 0.1;
}
.composite-line.highlighted .edge.real {
    stroke: magenta;
}
.composite-line.highlighted:not(.equal) .edge.real {
    marker-end: url('#arrowhead-highlight');
}

#arrowhead-highlight path {
    fill: magenta;
}

.edge.hoverhelper {
    opacity: 0;
}

.composite-line:hover .edge.hoverhelper {
    opacity: 0.5;
}
</style>
