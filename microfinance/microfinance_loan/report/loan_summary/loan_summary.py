# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from microfinance.microfinance_loan.doctype.loan.loan \
	import get_undisbersed_principal, get_outstanding_principal

def execute(filters=None):
	columns = [
			_("Posting Date") + ":Date:90",
			_("Loan ID") + ":Link/Loan:90",
			_("Customer") + ":Link/Customer:120",
			_("Sanctioned Amount") + ":Currency/currency:90",
			_("Disbursed Amount") + ":Currency/currency:90",
			_("Recovered Amount") + ":Currency/currency:90",
			_("Outstanding Amount") + ":Currency/currency:90",
		]
	result = frappe.db.sql("""
			SELECT posting_date, name, customer, loan_principal
			FROM `tabLoan`
		""")
	data = []
	for row in result:
		undisbursed = get_undisbersed_principal(row[1]) or 0
		outstanding = get_outstanding_principal(row[1]) or 0
		data.append(row + (
				row[3] - undisbursed,
				row[3] - undisbursed - outstanding,
				outstanding
			))

	return columns, data
