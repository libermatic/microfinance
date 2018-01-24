// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

async function set_outstanding(frm) {
  const { message: outstanding } = await frappe.call({
    method:
      'microfinance.microfinance_loan.doctype.loan.loan.get_outstanding_principal',
    args: {
      loan: frm.doc['loan'],
      posting_date: frm.doc['posting_date'] || frappe.datetime.nowdate(),
    },
  });
  frm.set_value('prev_outstanding', outstanding);
  frm.set_value('write_off_amount', null);
  frm.set_value('after_write_off', null);
}

frappe.ui.form.on('Loan Write Off', {
  loan: async function(frm) {
    set_outstanding(frm);
    const { message } = await frappe.db.get_value(
      'Loan',
      frm.doc['loan'],
      'customer'
    );
    frm.set_value('customer', message['customer']);
  },
  posting_date: set_outstanding,
  company: async function(frm) {
    const { message } = await frappe.db.get_value(
      'Company',
      frm.doc['company'] || frappe.defaults.get_default('company'),
      'write_off_account'
    );
    frm.set_value('write_off_account', message['write_off_account']);
  },
  write_off_amount: function(frm) {
    const { write_off_amount, prev_outstanding } = frm.doc;
    if (write_off_amount) {
      frm.set_value('after_write_off', prev_outstanding - write_off_amount);
    }
  },
});
