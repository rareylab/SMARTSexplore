import { render, screen } from '@testing-library/vue'
import { Modal } from '../../smartsexplore/frontend/components/modals'

const WrapperComponent = {
  components: { Modal },
  template: `
    <modal id="xyz" button-text="click this!">
      TEST MODAL CONTENT
    </modal>
  `
};

test('Modal renders button text and modal content', () => {
  render(WrapperComponent);
  //check whether screen shows message containing "info"
  expect(screen.queryAllByText(/click this!/i)).toBeTruthy();
  expect(screen.queryAllByText(/test modal content/i)).toBeTruthy();
});


