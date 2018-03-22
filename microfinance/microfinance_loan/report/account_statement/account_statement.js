// Copyright (c) 2016, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Account Statement'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      default: frappe.datetime.month_start(),
      reqd: 1,
      width: '60px',
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      default: frappe.datetime.month_end(),
      reqd: 1,
      width: '60px',
    },
    {
      fieldname: 'loan',
      label: __('Loan'),
      fieldtype: 'Link',
      options: 'Loan',
      get_query: function() {
        return { doctype: 'Loan', filters: { docstatus: 1 } };
      },
      on_change: async function() {
        const loan = frappe.query_report_filters_by_name['loan'].get_value();
        const { message = {} } = await frappe.db.get_value('Loan', loan, [
          'customer_name',
          'posting_date',
        ]);
        frappe.query_report_filters_by_name['customer_name'].set_value(
          message['customer_name']
        );
        frappe.query_report_filters_by_name['loan_start_date'].set_value(
          message['posting_date']
        );
      },
      reqd: 1,
    },
    {
      fieldname: 'customer_name',
      label: __('Customer Name'),
      fieldtype: 'Data',
      hidden: 1,
    },
    {
      fieldname: 'loan_start_date',
      label: __('Loan Start Date'),
      fieldtype: 'Date',
      hidden: 1,
    },
  ],
};
