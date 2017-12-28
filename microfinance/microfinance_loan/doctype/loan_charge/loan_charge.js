// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan Charge', {
  refresh: function(frm) {
    frm.fields_dict['account'].get_query = doc => ({
      filters: {
        root_type: 'Income',
        is_group: false,
      },
    });
  },
});
