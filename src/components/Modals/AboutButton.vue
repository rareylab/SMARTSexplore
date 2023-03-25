<template>
  <modal id="about-modal" button-text="Learn more">
        <h4>About SMARTSexplore</h4>
        <p>
            SMARTSexplore is a web-based chemical pattern network analysis tool that allows
            comparison of available SMARTS-libraries and allows uploading of .smiles-files for
            matching with SMARTS.
        </p>
        <p>This tool was created by Inken Fender, Pia Pluemer and Simon Welker, 2021.</p>
        <p>It was refined by Mike Nguyen in 2022.</p>
  </modal>
</template>

<script>
/* eslint max-len: */
/**
 * The about button of the app, containing a modal that explains the application to the user.
 */
import Modal from './Modal.vue';

export default {
  name: 'AboutButton',
  components: {Modal},
};
</script>

<style>
  .modal{
    padding:100;
    background-color: black;
}
</style>
