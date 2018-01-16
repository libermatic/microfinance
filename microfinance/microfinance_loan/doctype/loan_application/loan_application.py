# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from datetime import date
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import getdate, today, date_diff, add_days, add_months

class LoanApplication(Document):
	def before_submit(self):
		self.status = 'Open'

	def update_status(self, status):
		self.status = status
		self.save()


@frappe.whitelist()
def reject(name):
	'''Method to reject a Loan Application'''
	loan_application = frappe.get_doc('Loan Application', name)
	loan_application.update_status('Rejected')

@frappe.whitelist()
def approve(name, loan_no=None):
	'''Method to approve a Loan Application'''
	loan_application = frappe.get_doc('Loan Application', name)
	if loan_application.loan:
		loan = frappe.get_doc('Loan', loan_application.loan)
		loan.update_from_application(loan_application)
	else:
		def postproc(source, target):
			interest_income_account, interest_receivable_account, loan_account = frappe.get_value(
					'Loan Settings',
					None,
					['interest_income_account', 'interest_receivable_account', 'loan_account']
				)
			target.update({
					'loan_no': loan_no,
					'posting_date': today(),
					'loan_principal': source.amount,
					'loan_account': loan_account,
					'interest_income_account': interest_income_account,
					'interest_receivable_account': interest_receivable_account,
				})
			recovery_frequency, day, billing_day = frappe.get_value(
					'Loan Plan',
					loan_application.loan_plan,
					['recovery_frequency', 'day', 'billing_day']
				)
			billing_date = getdate(target.posting_date).replace(day=billing_day)
			if date_diff(billing_date, target.posting_date) < 0:
				if recovery_frequency == 'Weekly':
					add_days(billing_date, 7)
				elif recovery_frequency == 'Monthly':
					add_months(billing_date, 1)
			target.update({
					'billing_date': billing_date
				})
		fields = get_mapped_doc('Loan Application', name, {
				'Loan Application': {
						'doctype': 'Loan',
						'validation': { 'status': ['=', 'Open'] }
					}
			}, None, postproc)
		loan = frappe.get_doc(fields)
		loan.insert()
		loan_application.loan = loan.name
	loan_application.update_status('Approved')
	return loan_application.loan
