<template>
<g class="smarts-nodes">
    <SmartsNode
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
</template>

<script>
/* eslint max-len: */
import SmartsNode from './SmartsNode.vue';

export default {
  name: 'SmartsNodes',
  components: {SmartsNode},
  emits: ['nodeClick', 'nodeHover', 'nodeDblClick', 'nodeDrag', 'nodeDragStart', 'nodeDragEnd'],
  props: {
    nodes: Array,
    classFn: Function,
    colorFn: Function,
    styleFn: Function,
  },
};
</script>

<style>
</style>
