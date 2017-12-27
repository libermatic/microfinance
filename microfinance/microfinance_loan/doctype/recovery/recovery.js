// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Recovery', {
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
    frm.set_value('interest', interest_amount);
    frm.set_value(
      'amount',
      interest_amount + message['stipulated_recovery_amount']
    );
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
});
