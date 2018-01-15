# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.utils.data import getdate, today, date_diff
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_default_address
import math
from datetime import date

from microfinance.microfinance_loan.doctype.loan.loan_utils \
	import get_interval, get_periods

class Loan(Document):
	def before_submit(self):
		self.disbursement_status = 'Sanctioned'
		self.recovery_status = 'Not Started'
	def update_from_application(self, application):
		'''Method used by Loan application to add to sanctioned amount'''
		amount = flt(application.amount)
		if amount < 0:
			frappe.throw('Cannot decrease principal')
		self.loan_principal += amount
		if not self.calculation_slab == application.calculation_slab:
			self.calculation_slab = application.calculation_slab
		if self.disbursement_status == 'Fully Disbursed':
			self.disbursement_status = 'Partially Disbursed'
		self.save()

@frappe.whitelist()
def get_undisbursed_principal(loan=None):
	'''Gets undisbursed principal'''
	if not loan:
		return None
	loan_doc = frappe.get_value(
			'Loan',
			loan,
			['loan_principal', 'loan_account'],
			as_dict=True
		)
	conds = [
			"account = '{}'".format(loan_doc.get('loan_account')),
			"voucher_type = 'Disbursement'",
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan)
		]
	disbursed_principal = frappe.db.sql("""
			SELECT sum(debit)
			FROM `tabGL Entry`
			WHERE {}
		""".format(" AND ".join(conds)))[0][0] or 0
	return flt(loan_doc.get('loan_principal')) - disbursed_principal

@frappe.whitelist()
def get_outstanding_principal(loan, posting_date=today()):
	'''Get outstanding principal'''
	if not isinstance(posting_date, date):
		posting_date = getdate(posting_date)
	loan_account = frappe.get_value('Loan', loan, 'loan_account')
	cond = [
			"account = '{}'".format(loan_account),
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan),
			"posting_date <= '{}'".format(posting_date),
		]
	principal = frappe.db.sql("""
			SELECT sum(debit) - sum(credit)
			FROM `tabGL Entry`
			WHERE {}
		""".format(" AND ".join(cond)))[0][0] or 0
	return principal

@frappe.whitelist()
def get_recovered_principal(loan):
	'''Get recovered principal'''
	loan_account = frappe.get_value('Loan', loan, 'loan_account')

	conds = [
			"account = '{}'".format(loan_account),
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan)
		]
	recovered = frappe.db.sql("""
			SELECT sum(credit) - sum(debit)
			FROM `tabGL Entry`
			WHERE voucher_type = 'Recovery' AND {}
		""".format(" AND ".join(conds)))[0][0] or 0
	unrecorded = frappe.db.sql("""
			SELECT sum(credit)
			FROM `tabGL Entry`
			WHERE voucher_type = 'Disbursement' AND {}
		""".format(" AND ".join(conds)))[0][0] or 0
	return recovered + unrecorded

def get_interest(loan=None, start_date=today(), end_date=today()):
	'''Get interest amount'''
	if not loan:
		return None
	period = '{} - {}'.format(start_date, end_date)
	interest_receivable_account = frappe.get_value(
			'Loan',
			loan,
			'interest_receivable_account'
		)
	conds = [
			"account = '{}'".format(interest_receivable_account),
			"against = '{}'".format(period),
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan)
		]

	owed, paid = frappe.db.sql("""
			SELECT
				sum(debit) as owed,
				sum(credit) as paid
			FROM `tabGL Entry`
			WHERE {}
		""".format(" AND ".join(conds)))[0]

	owed, paid = flt(owed), flt(paid)
	if owed > 0:
		return owed - paid

	principal = get_outstanding_principal(loan, end_date)
	rate, slab = frappe.get_value('Loan', loan, ['rate_of_interest', 'calculation_slab'])
	if slab:
		principal = math.ceil(principal / slab) * slab
	return principal * rate / 100.0

@frappe.whitelist()
def get_billing_periods(loan=None, interval_date=today(), no_of_periods=5):
	'''Returns start and end date of a period along with interest of the period'''
	billing_date, posting_date = frappe.get_value(
			'Loan',
			loan,
			['billing_date', 'posting_date']
		)
	if date_diff(interval_date, posting_date) < 0:
		frappe.throw('Cannot get interest for period before the loan was submitted')
	intervals = get_periods(billing_date.day, interval_date, no_of_periods)

	def check_for_posting_date_and_get_interest(interval):
		if date_diff(interval.get('start_date'), posting_date) < 0:
			interval.update({ 'start_date': posting_date })
		interval.update({
				'interest': get_interest(
						loan,
						interval.get('start_date'),
						interval.get('end_date')
					)
			})
		return interval

	periods = map(
			check_for_posting_date_and_get_interest,
			filter(
					lambda x: date_diff(x.get('end_date'), posting_date) > 0,
					intervals
				)
		)

	return periods

@frappe.whitelist()
def get_interest_amount(loan=None, start_date=today(), end_date=today()):
	'''Get interest amount'''
	if not loan:
		return None
	paid_amount = frappe.db.sql("""
			SELECT sum(interest)
			FROM `tabRecovery`
			WHERE docstatus = 1
			AND loan = '{loan}'
			AND billing_period = '{start_date} - {end_date}'
		""".format(loan=loan, start_date=start_date, end_date=end_date))[0][0] or 0
	principal = get_outstanding_principal(loan, end_date)
	rate, slab = frappe.get_value('Loan', loan, ['rate_of_interest', 'calculation_slab'])
	if slab:
		principal = math.ceil(principal / slab) * slab
	interest = principal * rate / 100.0 - paid_amount
	if interest < 0:
		return 0
	return interest

@frappe.whitelist()
def get_customer_address(customer=None):
	'''Returns formatted address of Customer'''
	if not customer:
		return None
	address = frappe.get_value(
			'Address',
			get_default_address('Customer', customer),
			['address_line1', 'address_line2', 'city', 'county', 'state', 'pincode'],
			as_dict=True
		) or {}
	state = ' - '.join(filter(lambda x: not not x, [
			address.get('state'),
			address.get('pincode'),
		]))
	return ', '.join(filter(lambda x: not not x, [
			address.get('address_line1'),
			address.get('address_line2'),
			address.get('city'),
			address.get('county'),
			state,
		]))
