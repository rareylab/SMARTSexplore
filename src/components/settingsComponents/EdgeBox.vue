<template>
<div class="collapsible-header active">
    <i class="material-icons">trending_flat</i>Edge selection
</div>
<div class="collapsible-body">
    <div class="row">
        <div class="col s12">
            <div class="slider-container">
                <label>Similarity range</label>
                <div id="slider" ref="slider" :value="range"></div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col s8">
            <label class="display-block">Colorscale of current range</label>
            <div class="colorbar">
                <span class="colorbar-block" v-for="color in colorMap.colors" :key="color.id"
                    :style="{ background: color, width: colorbarBlockWidth }">
                </span>
            </div>
        </div>
        <div class="col s4">
            <label>
                Steps
                <input type="number"
                    :value="steps"
                    min="2"
                    max="10"
                    step="1"
                    @change="$emit('update:steps', parseInt($event.target.value))"/>
            </label>
        </div>
    </div>
</div>
</template>

<script>
/* eslint max-len: */

import noUiSlider from 'materialize-css/extras/noUiSlider/nouislider';

export default {
  name: 'EdgeBox',
  emits: ['update:range', 'update:steps'],
  /**
  * Props of the range slider.
  */
  props: {
    colorMap: Function,
    steps: Number,
    range: Array,
  },
  computed: {
    colorbarBlockWidth() {
      return 1.0/this.steps * 100 + '%'; // (1 / this.colorMap.colors.length) * 100 + '%';
    },
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
      start: [this.range[0], this.range[1]],
      step: 0.01,
      range: {
        'min': 0,
        'max': 1,
      },
      connect: true,
      orientation: 'horizontal',
      pips: {
        mode: 'range',
        density: 10,
      },
    });
    // triggered on end when handle is let go
    this.$refs.slider.noUiSlider.on('end', (values, handle) => {
      this.$emit('update:range', _.map(values, Number));
    });
  },
};

</script>

<style>
@import 'materialize-css/extras/noUiSlider/nouislider.css';
.row.range-slider {
    margin-bottom: 50px;
}

.colorbar {
    height: 25px;
    margin-top: 15px;
}
.colorbar .col {
    width: 100%;
    height: 30px;
}
.colorbar .colorbar-block {
    height: 100%;
    display: inline-block;
}

.slider-container {
    padding: 5px;
    padding-bottom: 35px;
}
.slider-container .noUi-pips-horizontal {
    height: auto;
}

.display-block {
    display: block;
}

</style>
