<template>
<copyable label="Source pattern:" :text="edge.source.pattern" />
<copyable label="Target pattern:" :text="edge.target.pattern" />
<copyable label="Pattern similarity:" :text="String(edge.spsim)" />

<template v-if="showMatches">
    <label>Molecule matches</label>
    <div class="molecule-matches">
        <span v-if="commonMatches.length">
            <pluralize string="common match" pluralString="common matches"
                :count="commonMatches.length"/>
            (of {{ edge.target.meta.matches.length }})
        </span>
        <span v-else>No common matches</span>

        <matches-grid v-if="commonMatches.length"
            :matches="commonMatches.concat(differentMatches)"
            :classFn="matchClassFn"
        />
    </div>
</template>
</template>

<script>
/* eslint max-len: */

/**
 * Vue component that displays information about a directed SMARTS-SMARTS subset edge.
 */

import Copyable from './Copyable.vue';
import MatchesGrid from './MatchesGrid.vue';
import Pluralize from './Pluralize.vue';

export default {
  name: 'SmartsSubsetEdgeInfo',
  components: {Copyable, MatchesGrid, Pluralize},
  /** Props of this component */
  props: {
    /** The Edge object to display */
    edge: Object,
    /** Whether to show molecule matches on the edge (based on data stored on its SMARTS) */
    showMatches: Boolean,
  },
  data() {
    return {
      /** Used for highlighting the matches
       * @param {match} match
       * @return {string}
      */
      matchClassFn(match) {
        if (match.kind == 'common') {
          return 'common-match';
        };
        if (match.kind == 'different') {
          return 'different-match';
        };
      },
    };
  },
  /**
   * Computed props of this component
   */
  computed: {
    /**
     * An array of the molecule matches that are *common to* both of this edge's SMARTS.
     * Returns nothing if the showMatches prop is not truthy.
     * @return {matches}
     */
    commonMatches() {
      const {edge, showMatches} = this;
      if (showMatches) {
        return _.map(
            _.intersectionBy(
                edge.source.meta.matches, edge.target.meta.matches,
                'molecule_id',
            ),
            (m) => {
              return {...m, 'kind': 'common'};
            },
        );
      }
      return null;
    },
    /**
     * An array of the molecule matches that are *different between* both of this edge's SMARTS.
     * Returns nothing if the showMatches prop is not truthy.
     * @return {matches}
     */
    differentMatches() {
      const {edge, showMatches} = this;
      if (showMatches) {
        return _.map(
            _.differenceBy(
                edge.target.meta.matches, edge.source.meta.matches,
                'molecule_id',
            ),
            (m) => {
              return {...m, 'kind': 'different'};
            },
        );
      }
      return null;
    },
  },
};
</script>
<style></style>
