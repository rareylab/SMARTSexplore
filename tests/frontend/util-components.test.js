import {render, fireEvent} from '@testing-library/vue';
import Pluralize from '../../src/components/ImageBoxComponents/Pluralize.vue';

test('Pluralize renders text with reasonable defaults', () => {
  let {queryByText} = render(Pluralize, {
    props: {
      string: 'nose',
      count: 0,
      pluralString: 'noses'},
  });
  expect(queryByText('0 noses')).not.toBe(null);

  queryByText = render(Pluralize, {props: {string: 'bonk', count: 21, pluralString: 'bonks'}}).queryByText;
  expect(queryByText('21 bonks')).not.toBe(null);

  queryByText = render(Pluralize, {props: {string: 'monki', count: 1, pluralString: 'monkis'}}).queryByText;
  expect(queryByText('1 monki')).not.toBe(null);

  queryByText = render(Pluralize, {props: {string: 'monki', count: 2, pluralString: 'monkis'}}).queryByText;
  expect(queryByText('2 monkis')).not.toBe(null);
});

test('Pluralize renders custom plural string correctly, if passed', () => {
  let props = {string: 'nose', pluralString: 'AFFE', count: 0};
  let queryByText = render(Pluralize, {props}).queryByText;
  expect(queryByText('0 AFFE')).not.toBe(null);

  props = {string: 'bonk', pluralString: 'AFFE', count: 21};
  queryByText = render(Pluralize, {props}).queryByText;
  expect(queryByText('21 AFFE')).not.toBe(null);

  props = {string: 'monki', pluralString: 'AFFE', count: 1};
  queryByText = render(Pluralize, {props}).queryByText;
  expect(queryByText('1 monki')).not.toBe(null);
});
