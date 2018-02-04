frappe.pages['calculate_principal'].on_page_load = async function(wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Calculate Loan Principal',
    single_column: true,
  });
  microfinance.CalculatePrincipal(page.main[0]);
};
