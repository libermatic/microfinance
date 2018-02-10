// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer', {
  refresh: async function(frm) {
    const { message } = await frappe.db.get_value(
      'Loanee Details',
      { customer: frm.doc['name'] },
      [
        'name',
        'department',
        'designation',
        'posting',
        'date_of_joining',
        'date_of_retirement',
        'net_salary_amount',
      ]
    );
    if (frm.fields_dict['loanee_details_html']) {
      microfinance.LoaneeDetails(
        frm.fields_dict['loanee_details_html'].wrapper,
        {
          ...message,
          on_add: function() {
            frappe.new_doc('Loanee Details', { customer: frm.doc['name'] });
          },
          on_edit: function() {
            frappe.set_route('Form', 'Loanee Details', message['name']);
          },
        }
      );
    }
  },
});
