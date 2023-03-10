<template>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<div class="settings-container">
    <ul ref="settingCollapsible" class="collapsible">
        <li class="active">
            <div class="collapsible-header active">
                Settings
            </div>
            <div class="collapsible-body">
                <ul ref="collapsible" class="collapsible">
                    <li class="active">
                        <InfoBox/>
                    </li>
                    <li class="active">
                        <FocusBox
                        v-model:selectOn="settings.selectOn"
                        v-model:maxDFSDepth="settings.maxDFSDepth"
                        v-model:nightMode="settings.nightMode"
                        />
                    </li>
                    <li class="active">
                        <NodeBox
                        v-model:librarySelection="settings.librarySelection"
                        v-model:searchString="settings.searchString"
                        :searchStringError="settings.searchStringError"
                        :libraryToColor="libraryToColor"
                        />
                    </li>
                    <li class="active">
                        <EdgeBox
                        v-model:steps="settings.edgeSimilarity.steps"
                        v-model:range="settings.edgeSimilarity.range"
                        :colorMap="colorMap"
                        />
                    </li>
                    <li class="active">
                        <UploadBox
                        v-model:showMatches="settings.showMatches"
                        :matchesLoaded="matchesLoaded"
                        @response="this.$emit('fileUploadResponse',$event)"
                        />
                    </li>
                </ul>
            </div>
        </li>
    </ul>
</div>

</template>

<script>
/* eslint max-len: */
// import M from 'materialize-css';
import InfoBox from './settingsComponents/InfoBox.vue';
import FocusBox from './settingsComponents/FocusBox.vue';
import NodeBox from './settingsComponents/NodeBox.vue';
import EdgeBox from './settingsComponents/EdgeBox.vue';
import UploadBox from './settingsComponents/UploadBox.vue';

export default {
  name: 'graphSettings',
  components: {
    InfoBox,
    FocusBox,
    NodeBox,
    EdgeBox,
    UploadBox,
  },
  emits: ['update:modelValue', 'fileUploadResponse'],
  props: {
    modelValue: Object,
    libraryToColor: Object,
    colorMap: Function,
    matchesLoaded: Boolean,
  },
  computed: {
    settings: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      },
    },
  },
  mounted() {
    // initialize the settingspanel to be collapsible
    this._settingCollapsible = M.Collapsible.init(this.$refs.settingCollapsible, {
      accordion: false,
    });
    // initialize the panel in the settings to be collapsible
    this._collapsible = M.Collapsible.init(this.$refs.collapsible, {
      accordion: false,
    });
  },
  beforeUnmount() {
    // destroy all collapsibles
    this._collapsible.destroy();
    this._settingCollapsible.destroy();
  },

};
</script>

<style>
/* suggest to browsers to use 3D acceleration for our SVG elements (CSS hack) */

/* Settings & info containers */

.settings-container, .info-container {
    position: fixed;
    border: 1px solid #ccc;
    background: white;
    box-shadow: 0 1px 1px rgba(0,0,0,0.15),
      0 2px 2px rgba(0,0,0,0.15),
      0 4px 4px rgba(0,0,0,0.15),
      0 8px 8px rgba(0,0,0,0.15);
    border-radius: 2px;

    max-height: 100%;
    overflow-y: auto;
}
.settings-container {
    width: 20%;
    min-width: 300px;
    top: .5rem;
    left: .5rem;
    height: auto;
    margin: 0;
    padding: 0;
}

/* Settings container: component styling */

.settings-container input {
    max-width: 100%;
}

.settings-container .collapsible .collapsible {
    margin: 0;
    padding: 0;
    box-shadow: none;
}

.settings-container .collapsible .collapsible .collapsible-body {
    padding: 1rem;
}

.settings-container .collapsible .collapsible .collapsible-body .row:last-of-type {
    margin-bottom: 2px;
}

/* Customized Materialize.css components / overrides */

.collapsible .collapsible-header {
    background: #ebebeb;
}

.collapsible .collapsible .collapsible-header {
    background: #f3f3f3;
}

.settings-container .collapsible{
    margin:0;
    padding:0;
}

.settings-container .collapsible .collapsible-body{
    padding:0;
}

</style>
