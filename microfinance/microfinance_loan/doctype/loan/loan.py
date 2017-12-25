# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model.document import Document
import math

class Loan(Document):
	def add_principal(self, amount):
		amount = flt(amount)
		if amount < 0:
			frappe.throw('Cannot decrease principal')
		self.loan_principal += amount
		self.save()

@frappe.whitelist()
def get_undisbersed_principal(loan):
	full_principal = frappe.get_value('Loan', loan, 'loan_principal')
	disbursed_principal = frappe.db.sql("""
			SELECT SUM(amount)
			FROM `tabDisbursement`
			WHERE docstatus=1 AND loan='{}'
		""".format(loan))[0][0]
	return flt(full_principal) - flt(disbursed_principal)

@frappe.whitelist()
def get_outstanding_principal(loan):
	loan_account = frappe.get_value('Loan', loan, 'loan_account')
	cond = [
			"account = '{}'".format(loan_account),
			"voucher_type = 'Journal Entry'",
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan)
		]
	principal = frappe.db.sql("""
			SELECT sum(debit) - sum(credit)
			FROM `tabGL Entry`
			WHERE {}
		""".format(" and ".join(cond)))[0][0]
	return principal

@frappe.whitelist()
def get_interest_amount(loan):
	principal = get_outstanding_principal(loan)
	rate, slab = frappe.get_value('Loan', loan, ['rate_of_interest', 'calculation_slab'])
	if slab:
		principal = math.ceil(principal / slab) * slab
	return principal * rate / 100.0
