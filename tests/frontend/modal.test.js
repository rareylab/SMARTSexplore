import { render, screen, fireEvent } from '@testing-library/vue'
import { mount } from '@vue/test-utils'
import { Modal } from '../../smartsexplore/frontend/components/modals'

///////////////WORK IN PROGRESS////////////////////////

const WrapperComponent = {
  components: { Modal },
  template: `
    <modal id="xyz" button-text="click this!">
      TEST MODAL CONTENT
    </modal>
  `
};

test('Modal renders button text and modal content', () => {
  let { container, queryAllByText } = render(WrapperComponent);
  //check whether screen shows message containing "info"
  expect(screen.queryAllByText(/click this!/i)).toBeTruthy();
  expect(screen.queryAllByText(/test modal content/i)).toBeTruthy();
});


