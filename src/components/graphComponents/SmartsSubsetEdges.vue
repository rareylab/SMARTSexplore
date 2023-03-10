<template>
<g class="subset-edges">
    <SmartsSubsetEdge v-for="edge in edges"
        :key="edge.id"
        :edge="edge"
        :classFn="classFn"
        :colorFn="colorFn"
        :styleFn="styleFn"
        @mouseover="$emit('edgeHover', { event: $event, edge: edge })"
        @click="$emit('edgeClick', { event: $event, edge: edge })"
    />
</g>
</template>

<script>
import SmartsSubsetEdge from './SmartsSubsetEdge.vue';

export default {
  name: 'SmartsSubsetEdges',
  components: {SmartsSubsetEdge},
  emits: ['edgeHover', 'edgeClick'],
  props: {
    edges: Object,
    classFn: Function,
    colorFn: Function,
    styleFn: Function,
  },
};

</script>

<style>

</style>
