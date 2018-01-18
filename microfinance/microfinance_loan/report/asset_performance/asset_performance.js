// Copyright (c) 2016, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Asset Performance'] = {
  filters: [
    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      default: frappe.defaults.get_user_default('Company'),
      reqd: 1,
    },
    {
      fieldname: 'loan_plan',
      label: __('Loan Plan'),
      fieldtype: 'Link',
      options: 'Loan Plan',
    },
    {
      fieldname: 'duration',
      label: __('Duration'),
      fieldtype: 'Select',
      options: 'Current Month\nLast 3 Months\nLast 6 Months',
      default: 'Current Month',
    },
    {
      fieldname: 'show_npas_only',
      label: __('Show NPAs Only'),
      fieldtype: 'Check',
    },
  ],
};
