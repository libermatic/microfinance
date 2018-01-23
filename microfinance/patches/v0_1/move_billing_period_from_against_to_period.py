# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def execute():
    frappe.reload_doctype('GL Entry')
    loans = frappe.get_all('Loan')
    frappe.db.sql("""
            UPDATE
                `tabGL Entry` as GLEntry,
                `tabLoan` as Loan
            SET
                GLEntry.period = GLEntry.against,
                GLEntry.against = NULL
            WHERE GLEntry.against IS NOT NULL
            AND GLEntry.period IS NULL
            AND Loan.name IN ({})
            AND (GLEntry.against_voucher = Loan.name OR GLEntry.voucher_no = Loan.name)
            AND GLEntry.account IN (Loan.interest_receivable_account, Loan.loan_account)
        """.format(", ".join(map(lambda x: "'{}'".format(x.get('name')), loans))))
