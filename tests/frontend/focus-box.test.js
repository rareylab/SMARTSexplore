import {mount} from '@vue/test-utils';
import {render, screen} from '@testing-library/vue';
import FocusBox from '../../src/components/settingsComponents/FocusBox.vue';

////////////////WORK IN PROGRESS////////////////////
test('Node fixation setting shows up on screen correctly', async () => {
  let {queryByText} = await render(FocusBox, {
    propsData: {
      selectOn: 'hover',
      maxDFSDepth: 3,
      nightMode: false,
    },
  });
  expect(screen.queryByText('hover')).toBeTruthy();
  expect(screen.queryByText('click')).toBeTruthy();
});

const NodeBoxWrapper = {
  data() {
    return {value: 'hover',
      maxDFSDepth: 3,
      nightMode: false,
    };
  },
  components: {FocusBox},
  template: `<FocusBox v-model:selectOn="value"
  v-model:maxDFSDepth="maxDFSDepth"
  v-model:nightMode="nightMode"/>`,
};

test('Node fixation renders correctly', async () => {
  const wrapper = mount(NodeBoxWrapper);
  expect(wrapper.vm.value).toEqual('hover');
  const clickEl = wrapper.get('input[type=radio][value=click]');
  await clickEl.trigger('click');
  expect(wrapper.vm.value).toEqual('click');
});

