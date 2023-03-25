<template>
<ArrowheadMarker  v-for="color in colors" :key="color.id"
    :color="color"
    :id="ids[color]"
/>
</template>

<script>
/* eslint max-len: */
/* eslint vue/no-mutating-props: */
import ArrowheadMarker from './ArrowheadMarker.vue';

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
  name: 'ArrowheadMarkers',
  components: {ArrowheadMarker},
  props: {
    colors: {
      type: Array,
      validator: (colors) => {
        return _.every(colors, (color) => color.startsWith('#'));
      },
    },
  },
  computed: {
    ids() {
      return _.fromPairs(
          _.map(this.colors,
              (color) => [color, `arrowhead-${getColorIdFromColor(color)}`],
          ));
    },
  },
};
</script>

<style>
</style>
