import { mount } from '@vue/test-utils'
import { render, screen } from '@testing-library/vue'
import { NodeFix } from '../../smartsexplore/frontend/components/node-fix'

test('Node fixation setting shows up on screen correctly', () => {
  render(NodeFix, {
    props: { modelValue: ''}
  });
  expect(screen.queryByText('hover')).toBeTruthy();
  expect(screen.queryByText('click')).toBeTruthy();
});

const NodeFixWrapper = {
  data() { return { value: 'hover' } },
  components: { NodeFix },
  template: `<node-fix v-model="value" />`
};

test('Node fixation renders correctly', async () => {
  const wrapper = mount(NodeFixWrapper);

  expect(wrapper.vm.value).toEqual('hover');
  const clickEl = wrapper.get('input[type=radio][value=click]');
  await clickEl.trigger('click');
  expect(wrapper.vm.value).toEqual('click');
});

