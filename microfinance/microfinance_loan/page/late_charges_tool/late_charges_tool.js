frappe.pages['late_charges_tool'].on_page_load = function(wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Interests and Charges Tool',
    single_column: true,
  });
  microfinance.LateChargesTool(page.main[0]);
  frappe.breadcrumbs.add('Microfinance Loan');
};
