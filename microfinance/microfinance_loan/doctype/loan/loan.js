// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan', {
  refresh: function(frm) {
    if (frm.doc.docstatus === 1) {
      const { disbursement_status, recovery_status } = frm.doc;
      if (['Sanctioned', 'Partially Disbursed'].includes(disbursement_status)) {
        frm
          .add_custom_button(__('Disburse'), function() {
            frm.make_new('Disbursement');
          })
          .addClass('btn-primary');
      }
      if (
        ['Partially Disbursed', 'Fully Disbursed'].includes(
          disbursement_status
        ) &&
        ['Not Started', 'In Progress'].includes(recovery_status)
      ) {
        frm
          .add_custom_button(__('Recover'), function() {
            frm.make_new('Recovery');
          })
          .addClass('btn-primary');
      }
    }
  },
  onload: async function(frm) {
    if (frm.doc.__islocal) {
      frm.set_df_property('disbursement_status', 'hidden', true);
      frm.set_df_property('recovery_status', 'hidden', true);
      const { message } = await frappe.db.get_value('Loan Settings', null, [
        'loan_account',
        'interest_income_account',
      ]);
      if (message) {
        const { loan_account, interest_income_account } = message;
        frm.set_value('loan_account', loan_account);
        frm.set_value('interest_income_account', interest_income_account);
      }
    }
  },
});
