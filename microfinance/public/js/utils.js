frappe.provide('microfinance');
frappe.provide('microfinance.utils');

microfinance.utils.check_billing_vs_due_date = function(billing_day, due_day) {
  return (
    moment(due_day).isAfter(billing_day) &&
    moment(due_day).date() > moment(billing_day).date()
  );
};
