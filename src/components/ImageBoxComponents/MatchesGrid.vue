<template>
<div class="molecule-grid">
    <span v-for="match in matches" :key="match.id"
        :class="'molecule ' + classFn(match)"
        :title="match.molecule_name"
    >
        <label>{{ match.molecule_name }}</label>
        <img :src="moleculeHref(match)" />
    </span>
</div>
</template>

<script>
/* eslint max-len: */

/**
 * A Vue component that renders a grid of matches, optionally with custom CSS classes attached
 * to each rendered match, based on an arbitrary function's return values.
 */

export default {
  props: {
    /**
     * An array of matches, which must each be an object containing a ``molecule_name`` (string)
     * and a ``molecule_id`` (integer).
     * @type {array}
     */
    matches: {
      type: Array,
      validator: (val) => _.every(val,
          (match) => 'molecule_name' in match && 'molecule_id' in match && // && 'molecule_set_id' in match
          typeof match.molecule_name == 'string' &&
          (match.molecule_id|0) == match.molecule_id,
      ),
    },
    /**
     * An optional function that associates a CSS class (or multiple, in one space-separated
     * string) with every rendered molecule match.
     * @type {(function(Node): string)}
     */
    classFn: {
      type: Function,
      default: (match) => '',
    },
  },

  /**
   * The methods of MatchesGrid.
   */
  methods: {
    /**
     * Gets the appropriate image URL given a molecule id. Doesn't do any validation, neither
     * for existence nor for input data.
     * @param {integer} match The molecule ID to get an image URL for.
     * @return {string} The image URL for that molecule.
     */
    moleculeHref(match) {
      return `http://localhost:5000/molecules/images/${match.molecule_id}`;
    },
  },
};

</script>

<style>
/* Molecule matches */

.molecule-grid {
    max-height: 30vh;
    overflow: auto;
    margin-top: 10px;
}
.molecule-grid .molecule {
    display: inline-block;
    vertical-align: middle;
    width: calc(50% - 10px);
    border: 1px solid rgba(0,0,0,.3);
    border-radius: 3px;
    padding: 5px;
    padding-top: 0;
    margin-right: 10px;
    margin-bottom: 10px;
}
.molecule-grid .molecule img {
    width: 100%;
    height: auto;
    margin-top: 5px;
}
.molecule-grid .molecule label {
    display: inline-block;
    margin-bottom: 5px;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
}

.molecule-grid .molecule.common-match {
    border-color: limegreen;
}
.molecule-grid .molecule.different-match {
    border-color: orangered;
}
</style>
