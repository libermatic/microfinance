// Copyright (c) 2016, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Asset Health'] = {
  filters: [
    {
      fieldname: 'customer',
      label: __('Customer'),
      fieldtype: 'Link',
      options: 'Customer',
    },
    {
      fieldname: 'loan',
      label: __('Loan'),
      fieldtype: 'Link',
      options: 'Loan',
      get_query: doc => ({ filters: { docstatus: 1 } }),
    },
    {
      fieldname: 'display',
      label: __('Display'),
      fieldtype: 'Select',
      options: 'NPA Only\nExisting Loans\nAll Loans',
      default: 'NPA Only',
    },
  ],
};
