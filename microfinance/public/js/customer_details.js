// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer', {
  refresh: async function(frm) {
    const { message: data } = await frappe.db.get_value(
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
      $(frm.fields_dict['loanee_details_html'].wrapper)
        .html(frappe.render_template('loanee_details', data))
        .find('.btn-loanee_details')
        .on('click', function() {
          frappe.new_doc('Loanee Details');
        });
    }
  },
});
