import * as M from 'materialize-css/dist/js/materialize.min.js'

const UploadBox = {
    name: 'uploadBox',
    emits: ['response'],
    data() {
        return {
            loading: false,
            files: null,
        };
    },
    props: {
        message: String,
        targetUrl: String
    },
    methods: {
        async uploadFile (event) {
            this.loading = true;
            const { target } = event;

            this._file = target.files[0];
            const data = new FormData();
            data.append('file', this._file, this._file.name);

            const request = new Request(this.targetUrl, {
                method: 'post',
                body: data
            })

            try {
                const response = await fetch(request);
                const json = await response.json();
                const ok = response.ok;

                if(ok) {
                    this.$emit('response', json);
                    M.toast({ html: 'Molecule set upload finished!' })
                }
                else {
                    throw new Error(json.error || String(response.status));
                }
            } catch(err) {
                let msg = (err instanceof Error) ? err.message : err;
                if(!msg) msg = "Unknown reason"
                M.toast({ html: `Molecule set upload failed: ${msg}` });
            } finally {
                this.loading = false;
            }
        }
    },
    template: `
<div>
    <label>Upload molecule file (.smi, .SMILES) to match to SMARTSs</label>
    <form>
        <div class="form-group1">
            <input v-show="!loading" type="file" @change="uploadFile" />
            <span v-show="loading">Loading...</span>
        </div>
    </form>
</div>
`
};

export { UploadBox };
