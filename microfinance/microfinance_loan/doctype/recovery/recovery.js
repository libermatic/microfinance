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
  const { loan, posting_date } = frm.doc;
  if (loan && posting_date) {
    const [{ message = {} }, { message: periods = [] }] = await Promise.all([
      frappe.db.get_value('Loan', loan, 'stipulated_recovery_amount'),
      frappe.call({
        method:
          'microfinance.microfinance_loan.doctype.loan.loan.get_billing_periods',
        args: { loan, interval_date: posting_date, no_of_periods: 1 },
      }),
    ]);

    const { stipulated_recovery_amount = 0 } = message;
    frm.set_value('principal', stipulated_recovery_amount);

    let interval = {};
    if (periods.length === 1) {
      interval = periods[0];
    }
    const { start_date, end_date, interest = 0 } = interval;
    if (start_date && end_date) {
      frm.set_value('billing_period', `${start_date} - ${end_date}`);
    }
    frm.set_value('interest', interest);
  } else {
    frm.set_value('billing_period', null);
    frm.set_value('interest', null);
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
  refresh: function(frm) {
    frm.fields_dict['loan'].get_query = doc => ({
      filters: { docstatus: 1 },
    });
    frappe.ui.form.on('Other Loan Charge', {
      charge_amount: calculate_total,
      loan_charges_remove: calculate_total,
    });
  },
  onload: async function(frm) {
    this.loading = new microfinance.utils.LoadingHandler();
    if (frm.doc.__islocal) {
      try {
        this.loading.append('settings');
        const { message } = await frappe.db.get_value(
          'Loan Settings',
          null,
          'mode_of_payment'
        );
        if (message) {
          const { mode_of_payment } = message;
          frm.set_value('mode_of_payment', mode_of_payment);
        }
      } catch (e) {
        frappe.throw(e.toString());
      } finally {
        this.loading.remove('settings');
      }
    }
    toggle_cheque_fields(frm);
  },
  loan: async function(frm) {
    try {
      this.loading.append('amount');
      const [{ message = {} }] = await Promise.all([
        frappe.db.get_value('Loan', frm.doc['loan'], 'customer'),
        get_amount_and_period(frm),
      ]);
      frm.set_value('customer', message['customer']);
    } catch (e) {
      frappe.throw(e.toString());
    } finally {
      this.loading.remove('amount');
    }
  },
  posting_date: async function(frm) {
    try {
      this.loading.append('period');
      await get_amount_and_period(frm);
    } catch (e) {
    } finally {
      this.loading.remove('period');
    }
  },
  principal: calculate_amount,
  interest: calculate_amount,
  amount: calculate_total,
  select_interval: function(frm) {
    if (frm.doc['loan']) {
      const dialog = new microfinance.utils.BillingPeriodDialog({
        frm,
        on_select: ({ period, interest }) => {
          frm.set_value('billing_period', period);
          frm.set_value('interest', interest);
        },
      });
      dialog.show();
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
