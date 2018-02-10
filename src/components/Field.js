// @flow

export type FieldType = {
  label?: string,
  fieldname?: string,
  options?: string,
  value?: mixed,
  fieldtype: 'Currency' | 'Date' | 'Link' | 'Column Break',
};

// eslint-disable-next-line
export default (props: FieldType) => null;
