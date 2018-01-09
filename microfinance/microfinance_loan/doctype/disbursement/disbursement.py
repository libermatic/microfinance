# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
from frappe.utils.data import fmt_money

from microfinance.microfinance_loan.doctype.loan.loan import get_undisbursed_principal

class Disbursement(AccountsController):
	def validate(self):
		if self.amount > get_undisbursed_principal(self.loan):
			frappe.throw(_("Disbursed amount cannot exceed the sanctioned amount"))
		if self.recovered_amount >= self.amount:
			frappe.throw(_("Recovered amount cannot be equal to or exceed the disbursed amount"))
	def on_submit(self):
		self.journal_entry = self.make_jv_entry()
		self.save()
		self.update_loan_status()

	def on_cancel(self):
		je = frappe.get_doc('Journal Entry', self.journal_entry)
		je.cancel()
		self.update_loan_status()

	def make_jv_entry(self):
		self.check_permission('write')
		je = frappe.new_doc('Journal Entry')
		je.title = self.customer
		if self.mode_of_payment == 'Cash':
			je.voucher_type = 'Cash Entry'
		elif self.mode_of_payment in ['Cheque', 'Bank Draft', 'Wire Transfer']:
			je.voucher_type = 'Bank Entry'
			je.cheque_no = self.cheque_no
			je.cheque_date = self.cheque_date
		elif self.mode_of_payment == 'Credit Card':
			je.voucher_type = 'Credit Card Entry'
		else:
			je.voucher_type = 'Journal Entry'
		je.user_remark = _('Against Loan: {0}. Disbursement Doc: {1}').format(self.loan, self.name)
		je.company = self.company
		je.posting_date = self.posting_date
		account_amt_list = []
		amount = self.amount
		transaction_details = 'Disbursement'
		if self.recovered_partially:
			amount -= self.recovered_amount
			transaction_details = 'Opening for original {}'.format(fmt_money(
					self.amount,
					precision=0,
					currency=frappe.defaults.get_user_default('currency')
				))
		account_amt_list.append({
				'account': self.payment_account,
				'credit_in_account_currency': amount,
				'reference_type': 'Loan',
				'reference_name': self.loan,
				'transaction_details': transaction_details
			})
		account_amt_list.append({
				'account': self.loan_account,
				'debit_in_account_currency': amount,
				'reference_type': 'Loan',
				'reference_name': self.loan,
			})
		if self.loan_charges:
			for row in self.loan_charges:
				account_amt_list[0]['credit_in_account_currency'] -= row.charge_amount
				account_amt_list.append({
						'account': row.charge_account,
						'credit_in_account_currency': row.charge_amount,
						'reference_type': 'Loan',
						'reference_name': self.loan,
						'transaction_details': row.charge
					})
		je.set("accounts", account_amt_list)
		je.insert()
		je.submit()
		return je.name

	def update_loan_status(self):
		'''Method to update disbursement_status of Loan'''
		loan_principal, disbursement_status = frappe.get_value(
				'Loan',
				self.loan,
				['loan_principal', 'disbursement_status']
			)
		undisbursed_principal = get_undisbursed_principal(self.loan)
		loan = frappe.get_doc('Loan', self.loan)
		if undisbursed_principal <= loan_principal:
			if undisbursed_principal == loan_principal and disbursement_status != 'Sanctioned':
				loan.disbursement_status = 'Sanctioned'
			elif undisbursed_principal > 0 and disbursement_status != 'Partially Disbursed':
				loan.disbursement_status = 'Partially Disbursed'
			else:
				loan.disbursement_status = 'Fully Disbursed'
			return loan.save()
		return loan.name
