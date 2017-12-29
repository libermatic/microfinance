# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from microfinance.microfinance_loan.doctype.loan.loan \
	import get_outstanding_principal, get_interest_amount

def execute(filters=None):
	columns = [
			_("Customer") + ":Link/Customer:120",
			_("Loan ID") + ":Link/Loan:90",
			_("Loan Plan") + ":Link/Loan Plan:90",
			_("Outstanding Amount") + ":Currency/currency:90",
			_("Interest") + ":Currency/currency:90",
		]
	result = frappe.db.sql("""
			SELECT customer, name, loan_plan
			FROM `tabLoan`
		""")
	data = []
	for row in result:
		outstanding = get_outstanding_principal(row[1]) or 0
		interest = get_interest_amount(row[1]) or 0
		data.append(row + (
				outstanding,
				interest,
			))
	return columns, data
