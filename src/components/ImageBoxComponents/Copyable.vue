<template>
<label>
    {{ label }}
    <div>
        <input class="with-icon-btn" type="text" disabled="disabled" :value="text" ref="input" />
        <button class="icon-btn icon-btn-right btn-flat waves-effect"
            ref="clipboardButton"
            :data-clipboard-text="text">
            <i class="material-icons">content_copy</i>
        </button>
    </div>
</label>
</template>

<script>
/* eslint max-len: */
import ClipboardJS from 'clipboard';

export default {
  name: 'copyableLabel',
  props: {
    label: String,
    text: String,
  },
  mounted() {
    this._clipboardJS = new ClipboardJS(this.$refs.clipboardButton);
  },
  beforeUnmount() {
    this._clipboardJS.destroy();
  },
};
</script>

<style>
input.with-icon-btn {
    width: calc(100% - 36px) !important;
}
.btn-flat.icon-btn {
    padding: 0;
    width: 36px;
    text-align: center;
    border-radius: 100%;
}
.icon-btn-right {
    margin-right: -6px;
    margin-top: 6px;
    float: right;
}
.icon-btn-left {
    margin-left: -6px;
    float: left;
    margin-top: 6px;
}
</style>
