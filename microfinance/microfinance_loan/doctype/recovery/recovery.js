// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

function calculate_total(frm) {
  const { amount = 0, loan_charges = [] } = frm.doc;
  frm.set_value(
    'total',
    amount + loan_charges.reduce((a, { charge_amount: x }) => a + x, 0)
  );
}

frappe.ui.form.on('Recovery', {
  refresh: function() {
    frappe.ui.form.on('Recovery Charge', {
      charge_amount: calculate_total,
      loan_charges_remove: calculate_total,
    });
  },
  onload: async function(frm) {
    if (frm.doc.__islocal) {
      const { message } = await frappe.db.get_value('Loan Settings', null, [
        'mode_of_payment',
      ]);
      if (message) {
        const { mode_of_payment, loan_account } = message;
        frm.set_value('mode_of_payment', mode_of_payment);
      }
    }
  },
  loan: async function(frm) {
    const [{ message: interest_amount = 0 }, { message }] = await Promise.all([
      frappe.call({
        method:
          'microfinance.microfinance_loan.doctype.loan.loan.get_interest_amount',
        args: {
          loan: frm.doc.loan,
        },
      }),
      frappe.db.get_value(
        'Loan',
        frm.doc['loan'],
        'stipulated_recovery_amount'
      ),
    ]);
    const { stipulated_recovery_amount = 0 } = message || {};
    frm.set_value('interest', interest_amount);
    frm.set_value('principal', stipulated_recovery_amount);
    frm.set_value('amount', interest_amount + stipulated_recovery_amount);
  },
  mode_of_payment: async function(frm) {
    const { message } = await frappe.call({
      method:
        'erpnext.accounts.doctype.sales_invoice.sales_invoice.get_bank_cash_account',
      args: {
        mode_of_payment: frm.doc.mode_of_payment,
        company: frm.doc.company,
      },
    });
    if (message) {
      frm.set_value('payment_account', message.account);
    }
  },
  amount: function(frm) {
    const { amount, interest } = frm.doc;
    frm.set_value('principal', amount - interest);
    calculate_total(frm);
  },
  onsubmit: calculate_total,
});
