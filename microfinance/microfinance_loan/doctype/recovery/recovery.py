# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.utils.data import fmt_money

from microfinance.microfinance_loan.doctype.loan.loan \
	import get_outstanding_principal, get_billing_period

class Recovery(AccountsController):
	def validate(self):
		outstanding_principal = get_outstanding_principal(self.loan, self.posting_date)
		if self.amount > outstanding_principal + flt(self.interest):
			frappe.throw(_(
					"Cannot recover more that the outstanding principal: {}"
						.format(outstanding_principal)
				))

	def on_submit(self):
		self.make_gl_entries()
		self.update_loan_status()

	def on_cancel(self):
		self.make_gl_entries(cancel=True)
		self.update_loan_status()

	def make_gl_entries(self, cancel=0, adv_adj=0):
		gl_entries = []
		if self.interest:
			self.add_party_gl_entries(gl_entries)
		self.add_loan_gl_entries(gl_entries)
		make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj)
		if len(self.loan_charges) > 0:
			gl_entries = self.add_charges_gl_entries()
			make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj, merge_entries=False)

	def get_gl_dict(self, args):
		gl_dict = frappe._dict({
				'against_voucher_type': 'Loan',
				'against_voucher': self.loan
			})
		gl_dict.update(args)
		return super(Recovery, self).get_gl_dict(gl_dict)

	def add_party_gl_entries(self, gl_entries):
		gl_entries.append(
				self.get_gl_dict({
						'account': self.interest_receivable_account,
						'debit': self.interest,
						'party_type': 'Customer',
						'party': self.customer,
					})
			)
		gl_entries.append(
				self.get_gl_dict({
						'account': self.interest_receivable_account,
						'credit': self.interest,
						'party_type': 'Customer',
						'party': self.customer,
					})
			)
	def add_loan_gl_entries(self, gl_entries):
		capital = self.amount - self.interest
		gl_entries.append(
				self.get_gl_dict({
						'account': self.loan_account,
						'credit': capital,
					})
			)
		gl_entries.append(
				self.get_gl_dict({
						'account': self.interest_income_account,
						'credit': self.interest,
						'cost_center': frappe.db.get_value('Loan Settings', None, 'cost_center'),
						'remarks': 'Interest for period: {}'.format(self.billing_period)
					})
			)
		remarks = 'Payment received'
		if capital:
			remarks += '. Capital: {}'.format(fmt_money(
					capital,
					precision=0,
					currency=frappe.defaults.get_user_default('currency')
				))
		gl_entries.append(
				self.get_gl_dict({
						'account': self.payment_account,
						'debit': self.amount,
						'against': self.customer,
						'remarks': remarks
					})
			)
	def add_charges_gl_entries(self):
		gl_entries = []
		total = 0
		cost_center = frappe.db.get_value('Loan Settings', None, 'cost_center')
		for row in self.loan_charges:
			total += row.charge_amount
			gl_entries.append(
					self.get_gl_dict({
							'account': row.charge_account,
							'credit': row.charge_amount,
							'cost_center': cost_center,
							'remarks': row.charge
						})
				)
		gl_entries.append(
				self.get_gl_dict({
						'account': self.payment_account,
						'debit': total,
						'against': self.customer,
					})
			)
		return gl_entries

	def update_loan_status(self):
		'''Method update recovery_status of Loan'''
		disbursement_status, loan_principal, recovery_status = frappe.get_value(
				'Loan',
				self.loan,
				['disbursement_status', 'loan_principal', 'recovery_status']
			)
		outstanding_principal = get_outstanding_principal(self.loan)
		loan = frappe.get_doc('Loan', self.loan)
		do_save = False
		if disbursement_status == 'Fully Disbursed' and outstanding_principal == 0:
			loan.clear_date = self.posting_date
			loan.recovery_status = 'Repaid'
			do_save = True
		else:
			if outstanding_principal == loan_principal and recovery_status != 'Not Started':
				loan.recovery_status = 'Not Started'
				do_save = True
			elif recovery_status != 'In Progress':
				loan.recovery_status = 'In Progress'
				do_save = True
			if loan.clear_date:
				loan.clear_date = None
				do_save = True
		if do_save:
			return loan.save()
		return loan.name
