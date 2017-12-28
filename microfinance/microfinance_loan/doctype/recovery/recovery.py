# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController

from microfinance.microfinance_loan.doctype.loan.loan import get_outstanding_principal

class Recovery(AccountsController):
	def validate(self):
		outstanding_principal = get_outstanding_principal(self.loan) + self.interest
		if self.amount > outstanding_principal:
			frappe.throw(_(
					"Cannot recover more that the outstanding principal: {}"
						.format(outstanding_principal)
				))

	def on_submit(self):
		self.journal_entry = self.make_jv_entry()
		self.save()
		self.update_loan_status()

	def on_cancel(self):
		pass

	def make_jv_entry(self):
		self.check_permission('write')
		je = frappe.new_doc('Journal Entry')
		je.title = self.customer
		je.voucher_type = 'Cash Entry'
		je.user_remark = _('Against Loan: {0}. Recovery Doc: {1}').format(self.loan, self.name)
		je.company = self.company
		je.posting_date = self.posting_date
		account_amt_list = []
		account_amt_list.append({
				'account': self.payment_account,
				'debit_in_account_currency': self.amount,
				'reference_type': 'Loan',
				'reference_name': self.loan,
			})
		principal = self.amount
		if self.interest > 0:
			account_amt_list.append({
				'account': self.interest_income_account,
				'credit_in_account_currency': self.interest,
				'reference_type': 'Loan',
				'reference_name': self.loan,
			})
			principal = principal - self.interest
		if principal:
			account_amt_list.append({
					'account': self.loan_account,
					'credit_in_account_currency': self.amount - self.interest,
					'reference_type': 'Loan',
					'reference_name': self.loan,
				})
		if self.loan_charges:
			for row in self.loan_charges:
				account_amt_list[0]['debit_in_account_currency'] += row.charge_amount
				account_amt_list.append({
						'account': row.charge_account,
						'credit_in_account_currency': row.charge_amount,
						'reference_type': 'Loan',
						'reference_name': self.loan,
					})
		je.set("accounts", account_amt_list)
		je.insert()
		je.submit()
		return je.name

	def update_loan_status(self):
		disbursement_status, recovery_status = frappe.get_value(
				'Loan',
				self.loan,
				['disbursement_status', 'recovery_status']
			)
		outstanding_principal = get_outstanding_principal(self.loan)
		loan = frappe.get_doc('Loan', self.loan)
		if disbursement_status == 'Fully Disbursed' and outstanding_principal == 0:
			loan.recovery_status = 'Repaid'
		else:
			if recovery_status == 'In Progress':
				return None
			loan.recovery_status = 'In Progress'
		return loan.save()
