// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan Plan', {
  validate: function(frm) {
    if (frm.doc['recovery_frequency'] === 'Monthly') {
      const { billing_day, due_day } = frm.doc;
      if (!microfinance.utils.check_billing_vs_due_date(billing_day, due_day)) {
        frappe.throw(
          __('Due Day must after Billing Date and should be within 30 days')
        );
      }
    }
  },
  recovery_frequency: function(frm) {
    frm.set_value('day', null);
    frm.set_value('billing_day', null);
    frm.set_value('due_day', null);
    frm.set_df_property('day', 'reqd', 0);
    frm.set_df_property('billing_day', 'reqd', 0);
    frm.set_df_property('due_day', 'reqd', 0);
    const { recovery_frequency } = frm.doc;
    if (recovery_frequency === 'Weekly') {
      frm.set_df_property('day', 'reqd', 1);
    } else if (recovery_frequency === 'Monthly') {
      frm.set_df_property('billing_day', 'reqd', 1);
      frm.set_df_property('due_day', 'reqd', 1);
    }
  },
});
