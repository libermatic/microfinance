const color = { Open: 'lightblue', Rejected: 'red', Approved: 'green' };

frappe.listview_settings['Loan Application'] = {
  add_fields: ['status'],
  get_indicator: function({ status }) {
    if (status) {
      return [__(status), color[status], `status,=,${status}`];
    }
    return null;
  },
};
