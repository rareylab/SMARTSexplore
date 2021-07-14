import ClipboardJS from 'clipboard';

const Copyable = {
    name: 'copyable',
    props: {
        label: String,
        text: String
    },
    mounted() {
        this._clipboardJS = new ClipboardJS(this.$refs.clipboardButton);
    },
    beforeUnmount() {
        this._clipboardJS.destroy();
    },
    template: `
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
    `
};


const Pluralize = {
    props: {
        count: {
            type: Number,
            validator: Number.isInteger  // verify that it's an integer
        },
        string: String,
        pluralString: String
    },
    template: `{{ count }} {{ count === 1 ? string : pluralString_ }}`,
    computed: {
        pluralString_() {
            return this.pluralString ? this.pluralString : this.string + 's';
        }
    }
};


export { Copyable, Pluralize };