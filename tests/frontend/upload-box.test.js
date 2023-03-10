import {render, screen, fireEvent} from '@testing-library/vue';
import {mount} from '@vue/test-utils';

import fetch from 'jest-fetch-mock';
import UploadBox from '../../src/components/settingsComponents/UploadBox.vue';

///////////////WORK IN PROGRESS////////////////////////

test('Upload Box renders correctly on screen', () => {
  let {queryByText} = render(UploadBox, {
    props: {
      matchesLoaded: false,
      showMatches: false,
    },
  });
  // check whether screen shows message containing molecule file
  expect(screen.getByText(/molecule file/i)).toBeTruthy();
});


let wrapper;
let fileInput;
let exampleFile;
describe('upload box keeps "loading" property in sync and handles upload', () => {
  beforeEach( async () => {
    fetch.resetMocks();

    wrapper = mount(UploadBox, {
      props: {
        matchesLoaded: false,
        showMatches: false,
      }});
    fileInput = wrapper.get('input[type=file]');
    exampleFile = new File([new Blob(['c1ccccc1 benz'])], 'test.smi');
  });

  test('success by emitting "response" event', async () => {
    // expect loading as false
    expect(wrapper.vm.loading).toEqual(false);

    // trigger upload
    // hand-mock 'files' prop via defineProperty since the original is readonly
    Object.defineProperty(fileInput.element, 'files', {value: [exampleFile]});
    // let fetchMock return some kind of response
    fetch.once(JSON.stringify({'success': true}));
    // trigger the change event, which will trigger the component's uploadFile method
    const changeEvt = fileInput.trigger('change');
    changeEvt;
    // expect mocked fetch method to have been called, once
    expect(fetch.mock.calls.length).toEqual(1);

    // expect loading being changed to true, and back to false after event handled
    expect(wrapper.vm.loading).toEqual(true);
    await changeEvt;
    expect(wrapper.vm.loading).toEqual(false);

    // assert that 'response' event has been emitted
    expect(wrapper.emitted().response).toBeTruthy();
  });

  test('failure by displaying failure message and not emitting "response" event', async () => {
    // assert that the text "upload failed" is not initially present on the page
    expect(screen.queryByText(/upload failed/i)).toBeFalsy();

    // expect loading as false
    expect(wrapper.vm.loading).toEqual(false);

    // trigger upload
    // hand-mock 'files' prop via defineProperty since the original prop is readonly
    Object.defineProperty(fileInput.element, 'files', {value: [exampleFile]});
    // let fetchMock return a failed response
    fetch.mockReject(new Error('fake error message'));
    // trigger the change event, which will trigger the component's uploadFile method
    const changeEvt = fileInput.trigger('change');

    // expect mocked fetch method to have been called, once
    expect(fetch.mock.calls.length).toEqual(1);

    // expect loading being changed to true, and back to false after event handled
    expect(wrapper.vm.loading).toEqual(true);
    await changeEvt;
    expect(wrapper.vm.loading).toEqual(false);

    // assert that 'response' event has not been emitted
    expect(wrapper.emitted().response).toBeFalsy();

    // assert that the text "upload failed" is now present on the page
    expect(screen.queryByText(/upload failed/i)).toBeTruthy();
  });
});
