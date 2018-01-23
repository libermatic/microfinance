# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def execute():
    frappe.reload_doctype('GL Entry')
    frappe.db.sql("""
            UPDATE
                `tabGL Entry`
            SET
                against_voucher_type = 'Loan',
                against_voucher = voucher_no
            WHERE voucher_type = 'Loan'
            AND against_voucher_type IS NULL
            AND against_voucher IS NULL
        """)
