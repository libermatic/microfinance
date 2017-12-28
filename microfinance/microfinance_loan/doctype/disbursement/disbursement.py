# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController

from microfinance.microfinance_loan.doctype.loan.loan import get_undisbersed_principal

class Disbursement(AccountsController):
	def validate(self):
		if self.amount > get_undisbersed_principal(self.loan):
			frappe.throw(_("Disbursed amount cannot be greater than sanctioned amount"))
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
		je.user_remark = _('Against Loan: {0}').format(self.loan)
		je.company = self.company
		je.posting_date = self.posting_date
		account_amt_list = []
		account_amt_list.append({
				'account': self.loan_account,
				'debit_in_account_currency': self.amount,
				'reference_type': 'Loan',
				'reference_name': self.loan,
			})
		account_amt_list.append({
				'account': self.payment_account,
				'credit_in_account_currency': self.amount,
				'reference_type': 'Loan',
				'reference_name': self.loan,
			})
		je.set("accounts", account_amt_list)
		je.insert()
		je.submit()
		return je.name

	def update_loan_status(self):
		loan_principal, disbursement_status = frappe.get_value(
				'Loan',
				self.loan,
				['loan_principal', 'disbursement_status']
			)
		undisbersed_principal = get_undisbersed_principal(self.loan)
		if undisbersed_principal <= loan_principal:
			loan = frappe.get_doc('Loan', self.loan)
			if undisbersed_principal > 0:
				if disbursement_status == 'Partially Disbursed':
					return None
				loan.disbursement_status = 'Partially Disbursed'
			else:
				loan.disbursement_status = 'Fully Disbursed'
		return loan.save()
