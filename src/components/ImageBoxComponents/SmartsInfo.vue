<template>
    <copyable label="Pattern:" :text="smarts.pattern" />

    <template v-if="showMatches">
        <label>Molecule matches</label>
        <div class="molecule-matches">
            <span>
                Matching
                <pluralize string="molecule" :count="smarts.meta.matches.length"/>
            </span>
            <MatchesGrid v-if="smarts.meta.matches.length" :matches="smarts.meta.matches" />
        </div>
    </template>
</template>

<script>
/* eslint max-len: */

/**
 * Vue component that displays information about a SMARTS node.
 */

import Copyable from './Copyable.vue';
import MatchesGrid from './MatchesGrid.vue';
import Pluralize from './Pluralize.vue';

export default {
  name: 'SmartsInfo',
  components: {Copyable, MatchesGrid, Pluralize},
  props: {
    /** The SMARTS object to display */
    smarts: Object,
    /** Whether to show molecule matches of the SMARTS */
    showMatches: Boolean,
  },
};
</script>

<style>
</style>
