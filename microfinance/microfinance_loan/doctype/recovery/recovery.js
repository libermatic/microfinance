// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

function calculate_total(frm) {
  const { amount = 0, loan_charges = [] } = frm.doc;
  frm.set_value(
    'total',
    amount + loan_charges.reduce((a, { charge_amount: x = 0 }) => a + x, 0)
  );
}
function calculate_amount(frm) {
  const { principal = 0, interest = 0 } = frm.doc;
  frm.set_value('amount', principal + interest);
}

async function toggle_cheque_fields(frm) {
  const { payment_account } = frm.doc;
  if (payment_account) {
    const { message } = await frappe.db.get_value(
      'Account',
      payment_account,
      'account_type'
    );
    const show_field = message['account_type'] === 'Bank';
    frm.toggle_display(['cheque_no', 'cheque_date'], show_field);
    frm.toggle_reqd(['cheque_no', 'cheque_date'], show_field);
  }
}

async function get_amount_and_period(frm) {
  const { loan, interval_date } = frm.doc;
  const [{ message = {} }, { message: period = [] }] = await Promise.all([
    frappe.db.get_value('Loan', loan, 'stipulated_recovery_amount'),
    frappe.call({
      method:
        'microfinance.microfinance_loan.doctype.loan.loan.get_billing_period',
      args: { loan, interval_date },
    }),
  ]);
  const { stipulated_recovery_amount = 0 } = message;
  const [start_date, end_date] = period;
  const { message: interest_amount } = await frappe.call({
    method:
      'microfinance.microfinance_loan.doctype.loan.loan.get_interest_amount',
    args: { loan, start_date, end_date },
  });
  frm.set_value('interest', interest_amount);
  frm.set_value('principal', stipulated_recovery_amount);
  frm.set_value('billing_period', period.join(' - '));
}

class LoadingHandler {
  constructor() {
    this.entities = [];
  }
  append(item) {
    this.entities.push(item);
  }
  remove(item) {
    const idx = this.entities.findIndex(x => x === item);
    if (idx > -1) {
      this.entities.splice(idx, 1);
    }
  }
  is_awaiting() {
    return this.entities.length !== 0;
  }
}

frappe.ui.form.on('Recovery', {
  validate: function(frm) {
    if (this.loading.is_awaiting()) {
      frappe.throw(
        'There are still a few items being loaded. Please wait for a while and retry.'
      );
    }
    if (!frm.doc['total']) {
      frappe.throw('Cannot do transaction of zero values.');
    }
  },
  refresh: function() {
    frappe.ui.form.on('Other Loan Charge', {
      charge_amount: calculate_total,
      loan_charges_remove: calculate_total,
    });
  },
  onload: async function(frm) {
    this.loading = new LoadingHandler();
    if (frm.doc.__islocal) {
      try {
        this.loading.append('settings');
        const { message } = await frappe.db.get_value('Loan Settings', null, [
          'mode_of_payment',
        ]);
        if (message) {
          const { mode_of_payment, loan_account } = message;
          frm.set_value('mode_of_payment', mode_of_payment);
        }
      } catch (e) {
        frappe.throw(e.toString());
      } finally {
        this.loading.remove('settings');
      }
    }
    if (frm.doc.docstatus == 0) {
      frm.set_value('journal_entry', null);
    }
    toggle_cheque_fields(frm);
  },
  loan: async function(frm) {
    try {
      this.loading.append('amount');
      await get_amount_and_period(frm);
    } catch (e) {
      console.log(e);
      frappe.throw(e.toString());
    } finally {
      this.loading.remove('amount');
    }
  },
  posting_date: function(frm) {
    frm.set_value('interval_date', frm.doc['posting_date']);
  },
  principal: calculate_amount,
  interest: calculate_amount,
  amount: calculate_total,
  interval_date: async function(frm) {
    try {
      this.loading.append('amount');
      await get_amount_and_period(frm);
    } catch (e) {
      frappe.throw(e.toString());
    } finally {
      this.loading.remove('amount');
    }
  },
  mode_of_payment: async function(frm) {
    try {
      this.loading.append('account');
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
    } catch (e) {
      frappe.throw(e.toString());
    } finally {
      this.loading.remove('account');
    }
  },
  payment_account: toggle_cheque_fields,
  onsubmit: calculate_total,
});
