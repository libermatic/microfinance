# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from microfinance.microfinance_loan.doctype.loan.loan \
    import get_billing_period

@frappe.whitelist()
def execute():
    '''Generates and updates interval_date and billing_period for Recovery'''
    frappe.reload_doc('Microfinance Loan', 'doctype', 'Recovery')
    unpatched_docs = frappe.db.sql("""
            SELECT name, posting_date, loan, interval_date
            FROM `tabRecovery`
            WHERE billing_period IS NULL
        """, as_dict=True)
    for doc in unpatched_docs:
        start_date, end_date = get_billing_period(
                doc.get('loan'),
                doc.get('interval_date') or doc.get('posting_date')
            )
        billing_period = '{} - {}'.format(start_date, end_date)
        set_fields = ["billing_period = '{}'".format(billing_period)]
        if not doc.get('interval_date'):
            set_fields.append("interval_date = posting_date")
        frappe.db.sql("""
                UPDATE `tabRecovery`
                SET {0}
                WHERE name = '{1}'
            """.format(", ".join(set_fields), doc.get('name')))
