import {render, fireEvent} from '@testing-library/vue';
import _ from 'lodash';
import EdgeBox from '../../src/components/settingsComponents/EdgeBox.vue';

//////////////////WORK IN PROGRESS/////////////////////////////////

test('Range slider renders with default properties', () => {
  const {queryByText, container} = render(EdgeBox, {
    props: {
      colorMap: (a) => a,
      steps: 5,
      range: [0.65, 1],
    },
  });
  // screen shows 'Similarity range' as header and 0 and 1
  expect(queryByText('Similarity range')).toBeTruthy();
  expect(queryByText('0')).toBeTruthy();
  expect(queryByText('1')).toBeTruthy();
  // check whether handles exits
  const lowerHandle = container.querySelector('div.noUi-handle-lower');
  const upperHandle = container.querySelector('div.noUi-handle-upper');
  expect(lowerHandle).toBeTruthy();
  expect(upperHandle).toBeTruthy();
});

test('Range slider emits update:range when handles are clicked', async () => {
  const {container, emitted} = render(EdgeBox, {
    props: {
      colorMap: (a) => a,
      steps: 5,
      range: [0.65, 1],
    },
  });

  const lower = container.querySelector('.noUi-handle-lower');
  const upper = container.querySelector('.noUi-handle-upper');
  expect(lower).toBeTruthy();
  expect(upper).toBeTruthy();

  // await Promise.all(_.each([lower, upper], async (handle, i) => {
  //   await fireEvent.mouseDown(handle);
  //   await fireEvent.mouseUp(handle);

  //   const modelVal = emitted()['update:range'][i][0];
  //   // i-th event, first arg of event
  //   expect(modelVal).toBeTruthy();
  //   expect(modelVal).toBeInstanceOf(Array);
  //   expect(modelVal).toEqual([0.65, 1.0]);
  // }));

  // expect(emitted()['update:range'].length).toBe(2);
});

