# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.utils.data import getdate, today, add_months, add_days, date_diff, get_last_day
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_default_address
import math
from datetime import date

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
	full_principal = frappe.get_value('Loan', loan, 'loan_principal')
	disbursed_principal = frappe.db.sql("""
			SELECT SUM(amount)
			FROM `tabDisbursement`
			WHERE docstatus=1 AND loan='{}'
		""".format(loan))[0][0]
	return flt(full_principal) - flt(disbursed_principal)

@frappe.whitelist()
def get_outstanding_principal(loan, posting_date=today()):
	'''Get outstanding principal'''
	if not isinstance(posting_date, date):
		posting_date = getdate(posting_date)
	loan_account = frappe.get_value('Loan', loan, 'loan_account')
	cond = [
			"account = '{}'".format(loan_account),
			"voucher_type = 'Journal Entry'",
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
def get_recovered_principal(loan, posting_date=today()):
	'''Get recovered principal'''
	recovered = frappe.db.sql("""
			SELECT SUM(principal)
			FROM `tabRecovery`
			WHERE docstatus=1 AND loan='{}'
		""".format(loan))[0][0]
	return flt(recovered)

def get_interval(day_of_month, date_obj):
	'''Returns start and end date of the interval'''
	if not isinstance(date_obj, date):
		date_obj = getdate(date_obj)
	try:
		start_date = date_obj.replace(day=day_of_month)
	except ValueError:
		start_date = add_months(date_obj, -1).replace(day=day_of_month)
	if date_diff(date_obj, start_date) < 0:
		start_date = add_months(start_date, -1)
	try:
		end_date = date_obj.replace(day=day_of_month)
	except ValueError:
		end_date = get_last_day(date_obj)
	if date_diff(end_date, date_obj) <= 0:
		end_date = add_months(end_date, 1)
	if end_date.day >= day_of_month:
		end_date = add_days(end_date, -1)
	return start_date, end_date

@frappe.whitelist()
def get_billing_period(loan=None, interval_date=today()):
	'''Returns start and end date of a period'''
	if not loan:
		return None
	if not isinstance(interval_date, date):
		interval_date = getdate(interval_date)
	billing_date = frappe.get_value('Loan', loan, 'billing_date')
	billing_day = billing_date.day if billing_date else 1
	start_date, end_date = get_interval(day_of_month=billing_day, date_obj=interval_date)
	return start_date, end_date

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
