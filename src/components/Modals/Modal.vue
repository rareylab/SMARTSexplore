<template>
    <a class="waves-effect waves-light btn modal-trigger" :href="'#' + id">{{ buttonText }}</a>

    <!-- Modal Structure -->
    <div :id="id" class="modal" ref="modal">
        <div class="modal-content">
            <slot></slot>
        </div>
        <div class="modal-footer">
            <a href="#!" class="modal-close waves-effect waves-green btn-flat">Close</a>
        </div>
    </div>
</template>

<script>
/* eslint max-len: */
import M from 'materialize-css';

export default {
  name: 'basicModal',
  props: {
    id: String,
    buttonText: String,
  },
  mounted() {
    this._modal = M.Modal.init(this.$refs.modal);
  },
  beforeUnmount() {
    this._modal.destroy();
  },
};

</script>

<style>
.night-mode .modal-content {
    background-color: #2a2a2a;
}

.night-mode .modal .modal-footer{
    background-color: #2a2a2a;
}
</style>
