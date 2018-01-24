# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from microfinance.microfinance_loan.doctype.recovery.recovery import update_loan_status

class LoanWriteOff(AccountsController):
	def validate(self):
		if not self.write_off_account:
			frappe.throw(_("Please set up Write Off Account in Company doc."))

	def on_submit(self):
		self.make_gl_entries()
		update_loan_status(self.loan)

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
		update_loan_status(self.loan)

	def get_gl_dict(self, args):
		gl_dict = frappe._dict({
				'against_voucher_type': 'Loan',
				'against_voucher': self.loan
			})
		gl_dict.update(args)
		return super(LoanWriteOff, self).get_gl_dict(gl_dict)

	def make_gl_entries(self, cancel=0, adv_adj=0):
		gl_entries = [
				self.get_gl_dict({
						'account': self.loan_account,
						'credit': self.write_off_amount,
						'against': self.write_off_account,
					}),
				self.get_gl_dict({
						'account': self.write_off_account,
						'debit': self.write_off_amount,
						'cost_center': frappe.db.get_value('Loan Settings', None, 'cost_center'),
						'against': self.loan_account,
						'remarks': self.reason,
					})
			]
		make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj, merge_entries=False)
