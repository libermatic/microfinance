# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from datetime import date
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

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
			interest_income_account, loan_account = frappe.get_value(
					'Loan Settings',
					None,
					['interest_income_account', 'loan_account']
				)
			target.update({
				'loan_no': loan_no,
				'posting_date': date.today(),
				'loan_principal': source.amount,
				'loan_account': loan_account,
				'interest_income_account': interest_income_account
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
