import _ from 'lodash';

import noUiSlider from 'materialize-css/extras/noUiSlider/nouislider';
import 'materialize-css/extras/noUiSlider/nouislider.css';

/**
 * A bidirectional range slider component, wrapping Materialize's noUiSlider variant.
 **/
const RangeSlider = {
    name: 'RangeSlider',
    emits: ['update:modelValue'],
    /**
    * Props of the range slider.
    */
    props: {
        /**
         * The model value, which is an array of length 2, the currently chosen [min, max] interval.
         * @type {array}
         */
        modelValue: Array,
        /**
         * The minimum range value available to the user
         * @type {number}
         */
        min: Number,
        /**
         * The maximum range value available to the user
         * @type {number}
         */
        max: Number,
        /**
         * The step size between available values
         * @type {number}
         */
        step: Number,
        /**
         * The initially selected minimum value
         * @type {number}
         */
        startMin: Number,
        /**
         * The initially selected maximum value
         * @type {number}
         */
        startMax: Number,
    },
    /**
     * creates slider with materialize noUiSlider
     * with defaults as described in app.js
     * connect set to true so that current range is highlighted
     * orientation horizontal, pips describe labelling and ticks
     * under the range
     */
    mounted() {
        noUiSlider.create(this.$refs.slider, {
            start: [this.startMin, this.startMax],
            step: this.step,
            range: {
                'min': this.min,
                'max': this.max
            },
            connect: true,
            orientation: 'horizontal',
            pips: {
                mode: 'range',
                density: 10
            }
        });
        // triggered on end when handle is let go
        this.$refs.slider.noUiSlider.on('end', (values, handle) => {
            this.$emit('update:modelValue', _.map(values, Number));
        });
    },
    template: `
<div class="slider-container">
  <label>Similarity range</label>
   <div ref="slider" :value="modelValue" />
</div>
`
};

export { RangeSlider };
