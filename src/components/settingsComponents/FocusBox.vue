<template>
<div class="collapsible-header active">
    <i class="material-icons">my_location</i>Focus
</div>
<div class="collapsible-body">
    <div class="nodefix-container">
        <label>Select object on {{selectOn}} </label>
        <div class="row">
            <div class="col s6">
                <label>
                    <input class="with-gap" type="radio" name="mode" value="hover"
                        @click="$emit('update:selectOn', $event.target.value)"
                        :checked="selectOn=='hover'"/>
                    <span>hover</span>
                </label>
            </div>
            <div class="col s6">
                <label>
                    <input class="with-gap" type="radio" name="mode" value="click"
                        @click="$emit('update:selectOn', $event.target.value)"
                        :checked="selectOn=='click'" />
                    <span>click</span>
                </label>
            </div>
        </div>
    </div>
    <div class="row dfs-settings">
        <div class="col s6">
            <label>
                DFS depth
                <input type="number" v-bind="maxDFSDepth" min="1" max="10" step="1"
                @change="$emit('update:maxDFSDepth', Number($event.target.value))"
                />
            </label>
        </div>
        <div class="col s6">
            <div><label>Night mode</label></div>
            <label class="input-like">
                <input type="checkbox" v-bind="nightMode"
                @change="$emit('update:nightMode', $event.target.checked)"
                />
                <span>{{ nightMode ? 'En' : 'Dis' }}abled</span>
            </label>
        </div>
    </div>
</div>
</template>

<script>
/* eslint max-len: */
/* eslint vue/no-mutating-props: */
export default {
  name: 'FocusBox',
  props: {
    selectOn: {
      type: String,
      default: 'hover',
    },
    maxDFSDepth: Number,
    nightMode: Boolean,
  },
};
</script>

<style>
.input-like {
    display: inline-block;
    margin-top: 15px;
}
</style>
