// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan Plan', {
  validate: function(frm) {
    if (frm.doc['recovery_frequency'] === 'Monthly') {
      const { billing_day } = frm.doc;
      if (billing_day < 1 || billing_day > 28) {
        frappe.throw(__('Billing day can only be between 1 and 28'));
      }
    }
  },
  recovery_frequency: function(frm) {
    frm.set_value('day', null);
    frm.set_value('billing_day', null);
    frm.set_df_property('day', 'reqd', 0);
    frm.set_df_property('billing_day', 'reqd', 0);
    const { recovery_frequency } = frm.doc;
    if (recovery_frequency === 'Weekly') {
      frm.set_df_property('day', 'reqd', 1);
    } else if (recovery_frequency === 'Monthly') {
      frm.set_df_property('billing_day', 'reqd', 1);
    }
  },
});
