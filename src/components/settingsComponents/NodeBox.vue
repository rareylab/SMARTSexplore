<!-- eslint-disable vue/require-component-is -->
<template>
<div class="collapsible-header active">
    <i class="material-icons">adjust</i>Node selection
</div>
<div class="collapsible-body">
    <div class="row search">
        <div class="search-container input-field col s12">
            <i class="material-icons prefix">search</i>
            <input id="searchbar"
                :class="{'invalid': searchStringError}"
                :value="searchString"
                @change="$emit('update:searchString', $event.target.value)"
                type="text" />
            <label for="searchbar">Search nodes by name</label>
        </div>
    </div>

    <div class="row library-select">
        <div class="col s12">
            <label>
                Library selection:
                <a href="#" @click="selectAllLibraries">All</a> |
                <a href="#" @click="deselectAllLibraries">None</a>
            </label>

            <div class="row">
                <!-- FIXME horribly hacky, but what else should we do with this MaterializeCSS selector? -->
                <div class="col s12 l6 library-selector" v-for="libraryID in libraryIDs" :key="libraryID.id">
                    <component is="style">
                        [type=checkbox]#__library-checkbox-{{ libraryID }}:checked + span::after {
                            background-color: {{ libraryToColor[libraryID] }};
                            border-color: transparent;
                        }
                    </component>
                    <label>
                        <input type="checkbox" class="filled-in" v-model="librarySelection[libraryID]"
                            :id="'__library-checkbox-' + libraryID" />
                        <span>{{ libraryID }}</span>
                    </label>
                </div>
            </div>
        </div>
    </div>
    <div class="row reference-button">
        <div class="col s12">
            <reference-button/>
        </div>
    </div>
</div>

</template>

<script>
/* eslint max-len: */
/* eslint vue/no-mutating-props: */
import ReferenceButton from '../Modals/ReferenceButton.vue';

export default {
  name: 'NodeBox',
  components: {
    ReferenceButton,
  },
  props: {
    librarySelection: Object,
    libraryToColor: Object,
    searchStringError: Boolean,
    searchString: String,
  },
  computed: {
    libraryIDs() {
      if (this.librarySelection) {
        const result = _.sortBy(Object.keys(this.librarySelection));
        return result;
      }
      return null;
    },
  },
  methods: {
    selectAllLibraries() {
      Object.keys(this.librarySelection).forEach((k) => {
        this.librarySelection[k] = true;
      });
    },
    deselectAllLibraries() {
      Object.keys(this.librarySelection).forEach((k) => {
        this.librarySelection[k] = false;
      });
    },
  },
};
</script>

<style>
.search-bar {
    width: 100%;
    max-width: 100%;
}

.row.search {
    margin-bottom: 10px;
}

.row.search .search-container {
    margin-top: .5rem;
}

.search-container.input-field {
    margin-bottom: 0;
}

.row.library-select {
    margin-bottom: 0;
}
.library-select .col > label:first-of-type {
    display: block;
    margin-bottom: .5rem;
}
.library-select .row:last-of-type {
    margin-bottom: 0;
}
.library-select .library-selector {
    margin: .1rem 0;
}
.library-select .library-selector label span {
    /* describes text of checkbox */
    padding-left: 28px;
}
[type="radio"]:not(:checked) + span, [type="radio"]:checked + span {
    padding-left: 30px;
}
</style>
