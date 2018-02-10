// @flow

export type FieldType = {
  label: ?string,
  fieldname: ?string,
  options: ?string,
  value: ?mixed,
  fieldtype: 'Currency' | 'Date' | 'Link' | 'Column Break',
};

export type FieldNode = (props: FieldType) => void;

export default () => null;
