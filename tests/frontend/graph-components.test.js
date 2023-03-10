import {mount} from '@vue/test-utils';
import ArrowheadMarker from '../../src/components/graphComponents/ArrowheadMarker.vue';

test('ArrowheadMarker renders correct id and fill', () => {
  const wrapper = mount(ArrowheadMarker, {
    props: {
      color: 'hotpink',
      id: 'xyz',
    },
  });

  const marker = wrapper.get('marker');
  expect(marker.attributes('id')).toBe('xyz');

  const path = marker.get('path');
  expect(path.attributes('fill')).toBe('hotpink');
});
