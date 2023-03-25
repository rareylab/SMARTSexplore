<template>
{{ count }} {{ count === 1 ? string : pluralString_ }}
</template>

<script>
export default {
  name: 'pluralizeCount',
  props: {
    count: {
      type: Number,
      validator: (num) => (num | 0) == num, // verify that it's an integer
    },
    string: String,
    pluralString: String,
  },
  computed: {
    pluralString_() {
      return this.pluralString ? this.pluralString : this.string + 's';
    },
  },
};
</script>

<style>
</style>
