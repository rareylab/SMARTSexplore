<template>
<div class="collapsible-header active">
    <i class="material-icons">info_outline</i> Info
</div>
<div class="collapsible-body">
    <div class="row info">
        <label>SMARTSexplore is a network analysis tool [...]</label>
        <div class="row info button">
            <about-button/>
        </div>
    </div>
</div>
</template>

<script>
import AboutButton from '../Modals/AboutButton.vue';

export default {
  components: {
    AboutButton,
  },
  data() {
    return {
      isModalVisible: false,
    };
  },
  methods: {
    showModal() {
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
    },
  },
};
</script>

<style>
</style>
