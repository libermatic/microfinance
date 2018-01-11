// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

function reset_chart(frm) {
  const chart_area = frm.$wrapper.find('.form-graph');
  chart_area.empty().addClass('hidden');
}

async function render_chart(frm) {
  const chart_area = frm.$wrapper.find('.form-graph');
  chart_area.empty().removeClass('hidden');
  const { message: data } = await frappe.call({
    method:
      'microfinance.microfinance_loan.doctype.loan.loan_dashboard.get_loan_chart_data',
    args: { docname: frm.doc['name'] },
  });
  if (data) {
    const chart = new Chart({
      parent: chart_area.selector,
      type: 'percentage',
      data,
      colors: ['green', 'orange', 'blue'],
    });
    $(chart.container)
      .find('.title')
      .addClass('hidden');
    $(chart.container)
      .find('.sub-title')
      .addClass('hidden');
  }
}

frappe.ui.form.on('Loan', {
  refresh: function(frm) {
    reset_chart(frm);
    if (frm.doc.docstatus === 1) {
      render_chart(frm);
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
        const btn = frm.add_custom_button(__('Recover'), function() {
          frm.make_new('Recovery');
        });
        if (disbursement_status === 'Fully Disbursed')
          btn.addClass('btn-primary');
      }
    }
    if (frm.doc.docstatus > 0) {
      frm.page.add_menu_item(__('Account Statement'), function(e) {
        frappe.set_route('query-report', 'Account Statement', {
          loan: frm.doc['name'],
        });
      });
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
      ['recovery_frequency', 'day', 'billing_day']
    );
    const { recovery_frequency, day, billing_day } = message;
    frm.set_value('day', null);
    frm.set_value('billing_date', null);
    if (recovery_frequency === 'Weekly') {
      frm.set_value('day', day);
    } else if (recovery_frequency === 'Monthly') {
      const { posting_date } = frm.doc;
      const bd = moment(billing_day).date();
      const billing_date = moment(posting_date).date(bd);
      frm.set_value('billing_date', billing_date);
    }
  },
});
