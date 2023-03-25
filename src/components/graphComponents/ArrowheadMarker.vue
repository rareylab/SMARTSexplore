<template>
<marker
    :id="id" :refX="refX" refY="0" viewBox="0 -5 10 10"
    markerUnits="userSpaceOnUse" :markerWidth="size" :markerHeight="size"
    xoverflow="visible" orient="auto"
>
    <path d="M 0,-5 L 10,0 L 0,5 z" :fill="color" />
</marker>
</template>

<script>

export default {
  name: 'ArrowheadMarker',
  props: {
    color: {
      type: String,
      default: () => '',
    },
    refX: {
      type: Number,
      default: () => 14,
    },
    size: {
      type: Number,
      default: () => 25,
    },
    id: {
      type: String,
    },
  },
};
</script>

<style>
</style>
