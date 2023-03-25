<template>
<div class='collapsible-header active'>
    <i class='material-icons'>file_upload</i>Molecule Upload
</div>
<div class='collapsible-body'>
    <div class='row upload-box'>
        <div class='col s12'>
            <label>Upload molecule file (.smi, .SMILES) to match to SMARTSs</label>
            <form>
                <div class='form-group1'>
                    <input v-show='!loading' type='file' @change='uploadFile($event)' ref='uploader'/>
                    <span v-show='loading'>Loading...</span>
                </div>
            </form>
        </div>
        <div class='col s12 matches-toggle' v-if='matchesLoaded'>
            <label>
                <input :value='showMatches' type='checkbox' class='filled-in' checked
                @change='$emit("update:showMatches", $event.target.checked)'>
                <span>Show molecule matches</span>
            </label>
        </div>
    </div>
</div>
</template>

<script>

/* eslint max-len: */
import * as M from 'materialize-css/dist/js/materialize.min.js';

export default {
  name: 'uploadBox',
  emits: ['response', 'update:showMatches'],
  data() {
    return {
      moleculeSetUploadUrl: 'http://localhost:5000/molecules/upload',
      loading: false,
    };
  },
  props: {
    matchesLoaded: Boolean,
    showMatches: Boolean,
  },
  methods: {
    async uploadFile(event) {
      this.loading = true;
      const data = new FormData();

      const {target} = event;
      this._file = target.files[0];
      data.append('file', this._file, this._file.name);

      const request = new Request(this.moleculeSetUploadUrl, {
        method: 'post',
        body: data,
      });

      try {
        const response = await fetch(request);
        const json = await response.json();
        const ok = response.ok;

        if (ok) {
          this.$emit('response', json);
          window.M.toast({html: 'Molecule set upload finished!'});
        } else {
          throw new Error(json.error || String(response.status));
        }
      } catch (err) {
        let msg = (err instanceof Error) ? err.message : err;
        if (!msg) msg = 'Unknown reason';
        window.M.toast({html: `Molecule set upload failed: ${msg}`});
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
.upload-box button {
  margin-top: 10px;
}
.col.matches-toggle {
    padding-top: 1rem;
}
</style>
