# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def execute():
    frappe.reload_doctype('Loan')
    frappe.db.sql("""
            UPDATE
                `tabLoan`
            SET
                rate_of_late_charges = rate_of_interest
                against_voucher = voucher_no
            WHERE rate_of_late_charges IS NULL
        """)
