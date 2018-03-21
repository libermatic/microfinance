// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

function reset_chart(frm) {
  const chart_area = frm.$wrapper.find('.form-graph');
  chart_area.empty().addClass('hidden');
}

async function render_chart(frm) {
  const chart_area = frm.$wrapper.find('.form-graph');
  chart_area.empty();
  const { message: data } = await frappe.call({
    method:
      'microfinance.microfinance_loan.doctype.loan.loan_dashboard.get_loan_chart_data',
    args: { docname: frm.doc['name'] },
  });
  if (data) {
    const chart = new Chart({
      parent: chart_area[0],
      type: 'percentage',
      data,
      colors: ['green', 'orange', 'blue', 'grey'],
    });
    chart_area.removeClass('hidden');
    $(chart.container)
      .find('.title')
      .addClass('hidden');
    $(chart.container)
      .find('.sub-title')
      .addClass('hidden');
  }
}

async function set_billing_date(frm) {
  const { posting_date, loan_plan } = frm.doc;
  if (posting_date && loan_plan) {
    const { message = {} } = await frappe.db.get_value('Loan Plan', loan_plan, [
      'recovery_frequency',
      'billing_day',
    ]);
    const { recovery_frequency, billing_day } = message;
    let billing_date = moment(posting_date).date(billing_day);
    if (billing_date.isBefore(posting_date)) {
      if (recovery_frequency === 'Weekly') {
        billing_date.add(7, 'days');
      } else if (recovery_frequency === 'Monthly') {
        billing_date.add(1, 'months');
      }
    }
    frm.set_value('billing_date', billing_date);
  }
}

frappe.ui.form.on('Loan', {
  refresh: function(frm) {
    reset_chart(frm);
    if (frm.doc.docstatus === 1) {
      render_chart(frm);
      frm.set_df_property('loan_principal', 'read_only', 1);
      frm.set_df_property('stipulated_recovery_amount', 'read_only', 1);
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
      frm.page.add_menu_item(__('Convert Interests'), function(e) {
        frappe.prompt(
          [
            {
              fieldname: 'ht',
              fieldtype: 'HTML',
              read_only: 1,
              options:
                '<p><strong class="text-danger">Danger!</strong></p><p>This action cannot be undone. If there were any errors, this whole Loan and its subsequent Disbursements and Recoveries would have to be cancelled.</p>',
            },
            {
              fieldname: 'till_date',
              fieldtype: 'Date',
              label: 'Till Date',
              default: frappe.datetime.nowdate(),
              reqd: 1,
            },
          ],
          async function({ till_date }) {
            await frappe.call({
              method:
                'microfinance.microfinance_loan.doctype.loan.loan.convert_all_interests_till',
              args: { loan: frm.doc['name'], posting_date: till_date },
            });
            frappe.msgprint(
              'All pending interests processed. Please check account statement'
            );
          },
          'Convert Interests to Principal',
          'Okay'
        );
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
        [
          'loan_account',
          'interest_income_account',
          'interest_receivable_account',
        ]
      );
      if (settings) {
        const {
          loan_account,
          interest_income_account,
          interest_receivable_account,
        } = settings;
        frm.set_value('loan_account', loan_account);
        frm.set_value('interest_income_account', interest_income_account);
        frm.set_value(
          'interest_receivable_account',
          interest_receivable_account
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
  posting_date: set_billing_date,
  loan_plan: set_billing_date,
});
