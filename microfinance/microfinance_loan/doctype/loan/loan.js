// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

async function render_graph(frm) {
  const chart_area = frm.$wrapper.find('.form-graph');
  const { message: data } = await frappe.call({
    method:
      'microfinance.microfinance_loan.doctype.loan.loan_dashboard.get_loan_chart_data',
    args: { docname: frm.doc['name'] },
  });
  if (data) {
    chart_area.empty().removeClass('hidden');
    const chart = new Chart({
      parent: chart_area.selector,
      title: 'Principal Summary',
      data: data,
      type: 'percentage',
      colors: ['green', 'orange', 'blue'],
    });
  }
}

frappe.ui.form.on('Loan', {
  refresh: function(frm) {
    if (frm.doc.docstatus === 1) {
      render_graph(frm);
      frm.set_df_property('loan_principal', 'read_only', 1);
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
      const { message: settings } = await frappe.db.get_value(
        'Loan Settings',
        null,
        ['loan_account', 'interest_income_account']
      );
      if (settings) {
        const { loan_account, interest_income_account } = settings;
        frm.set_value('loan_account', loan_account);
        frm.set_value('interest_income_account', interest_income_account);
      }
      const { message: letter_head } = await frappe.db.get_value(
        'Letter Head',
        { is_default: 1 },
        'name'
      );
      frm.set_value('letter_head', letter_head['name']);
    }
  },
  validate: function(frm) {
    if (frm.doc['recovery_frequency'] === 'Monthly') {
      const { billing_date, due_date } = frm.doc;
      if (
        !microfinance.utils.check_billing_vs_due_date(billing_date, due_date)
      ) {
        frappe.throw(
          __('Due Day must after Billing Date and should be within 30 days')
        );
      }
    }
  },
  customer: async function(frm) {
    const { message: customer_address } = await frappe.call({
      method:
        'microfinance.microfinance_loan.doctype.loan.loan.get_customer_address',
      args: { customer: frm.doc['customer'] },
    });
    frm.set_value('customer_address', customer_address);
  },
  loan_plan: async function(frm) {
    const { message = {} } = await frappe.db.get_value(
      'Loan Plan',
      frm.doc['loan_plan'],
      ['recovery_frequency', 'day', 'billing_day', 'due_day']
    );
    const { recovery_frequency, day, billing_day, due_day } = message;
    frm.set_value('day', null);
    frm.set_value('billing_date', null);
    frm.set_value('due_date', null);
    if (recovery_frequency === 'Weekly') {
      frm.set_value('day', day);
    } else if (recovery_frequency === 'Monthly') {
      const { posting_date } = frm.doc;
      const bd = moment(billing_day).date();
      const dd_days_after_bd = moment(due_day).diff(billing_day, 'days');
      let billing_date = moment(posting_date).date(bd);
      let due_date = moment(billing_date).add(dd_days_after_bd, 'days');
      frm.set_value('billing_date', billing_date);
      frm.set_value('due_date', due_date);
    }
  },
});
