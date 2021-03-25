const NodeFix = {
    name: 'nodeFix',
    emits: ['update:modelValue'],
    props: {
      modelValue: String,
    },
    template: `
<div class="nodefix-container">
    <label>Select object on</label>
    <div class="row">
        <div class="col s6">
            <label>
                <input class="with-gap" type="radio" name="mode" value="hover"
                    @change="$emit('update:modelValue', $event.target.value)"
                    :checked="modelValue=='hover'"/>
                <span>hover</span>
            </label>
        </div>
        <div class="col s6">
            <label>
                <input class="with-gap" type="radio" name="mode" value="click"
                    @change="$emit('update:modelValue', $event.target.value)"
                    :checked="modelValue=='click'" />
                <span>click</span>
            </label>
        </div>
    </div>
</div>
`
};

export { NodeFix };
