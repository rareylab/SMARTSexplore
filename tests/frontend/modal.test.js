import {render, screen, fireEvent} from '@testing-library/vue';
import basicModal from '../../src/components/Modals/Modal.vue';

///////////////WORK IN PROGRESS////////////////////////

const WrapperComponent = {
  components: {basicModal},
  template: `
    <basicModal id="xyz" button-text="click this!">
      TEST MODAL CONTENT
    </basicModal>
  `,
};

test('Modal renders button text and modal content', () => {
  let {container, queryAllByText} = render(WrapperComponent);
  // check whether screen shows message containing "info"
  expect(screen.queryAllByText(/click this!/i)).toBeTruthy();
  expect(screen.queryAllByText(/test modal content/i)).toBeTruthy();
});


