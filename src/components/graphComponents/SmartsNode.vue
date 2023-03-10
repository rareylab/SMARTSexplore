<template>
<circle
    ref="node"
    class="node"
    :class="classFn(node)"
    r="15"
    :fill="colorFn(node)"
    :style="styleFn(node)"
    />
</template>

<script>
/* eslint max-len: */
import * as d3 from 'd3';

export default {
  name: 'SmartsNode',
  emits: ['nodeDrag', 'nodeDragStart', 'nodeDragEnd'],
  props: {
    node: Object,
    classFn: Function,
    colorFn: Function,
    styleFn: Function,
  },
  mounted() {
    const nodeDrag = d3.drag();
    nodeDrag
        .on('drag', (event) => this.$emit('nodeDrag', {event: event, node: this.node}))
        .on('start', (event) => this.$emit('nodeDragStart', {event: event, node: this.node}))
        .on('end', (event) => this.$emit('nodeDragEnd', {event: event, node: this.node}));
    d3.select(this.$refs.node).call(nodeDrag);
  },
};

</script>

<style>
.node {
    stroke-width: 3;
    stroke: black;
}
.node.transparent-border {
    stroke: rgba(0,0,0,0.15);
}
.node:hover {
    opacity: 1;
}
.node:not(:hover):not(.highlighted).muted {
    opacity: 0.1;
}
.node.highlighted {
    fill: magenta;
}
.node.node-fixed {
    stroke: #ee1eeb;
}
</style>
