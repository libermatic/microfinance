// @flow
import React, { Component } from 'react';
import snakeCase from 'lodash/snakeCase';

import type { FieldType, FieldNode } from './Field';

type Props = {
  children: Array<FieldNode>,
  onChange: any => void,
};

class FieldGroup extends Component<Props, {}> {
  form: ?HTMLFormElement;
  fieldGroup: frappe.ui.FieldGroup;

  componentDidMount() {
    const fields = this.props.children.map(child =>
      this.makeField(child.props)
    );
    this.fieldGroup = new frappe.ui.FieldGroup({
      fields,
      parent: this.form,
    });
    this.fieldGroup.make();
    this.fieldGroup.fields_list.forEach(field => {
      field.$input.on('blur', () => {
        this.props.onChange({ [field.df.fieldname]: field.get_value() });
      });
    });
    fields.forEach(({ fieldname, value }) => {
      if (value) {
        this.fieldGroup.set_value(fieldname, value);
      }
    });
  }
  componentDidUpdate() {
    this.getFieldValues(this.props.children).forEach(({ fieldname, value }) => {
      if (fieldname && value !== this.fieldGroup.get_value(fieldname)) {
        this.fieldGroup.set_value(fieldname, value);
      }
    });
  }

  makeField = (props: FieldType): FieldType => {
    let keys = { ...props };
    if (!props.fieldname && props.label) {
      keys = { ...keys, fieldname: snakeCase(props.label) };
    }
    return keys;
  };
  getFieldValues = (
    children: Array<FieldNode>
  ): Array<{ fieldname: ?string, value: ?mixed }> =>
    children.map(({ props }) => {
      const { fieldname, value } = this.makeField(props);
      return { fieldname, value };
    });

  render() {
    return <form ref={form => (this.form = form)} />;
  }
}

export default FieldGroup;
