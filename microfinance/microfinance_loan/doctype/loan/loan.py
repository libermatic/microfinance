# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.utils.data import getdate, today, add_months, date_diff, get_last_day
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_default_address
import math

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
def get_undisbursed_principal(loan):
	'''Gets undisbursed principal'''
	full_principal = frappe.get_value('Loan', loan, 'loan_principal')
	disbursed_principal = frappe.db.sql("""
			SELECT SUM(amount)
			FROM `tabDisbursement`
			WHERE docstatus=1 AND loan='{}'
		""".format(loan))[0][0]
	return flt(full_principal) - flt(disbursed_principal)

@frappe.whitelist()
def get_outstanding_principal(loan, date=today()):
	'''Get outstanding principal'''
	loan_account = frappe.get_value('Loan', loan, 'loan_account')
	cond = [
			"account = '{}'".format(loan_account),
			"voucher_type = 'Journal Entry'",
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan),
			"posting_date <= '{}'".format(date),
		]
	principal = frappe.db.sql("""
			SELECT sum(debit) - sum(credit)
			FROM `tabGL Entry`
			WHERE {}
		""".format(" AND ".join(cond)))[0][0] or 0
	return principal

def get_interval(day_of_month, date_obj):
	'''Returns start and end date of the interval'''
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
	if date_diff(end_date, date_obj) < 0:
		end_date = add_months(end_date, 1)
	return start_date, end_date

@frappe.whitelist()
def get_interest_amount(loan=None, posting_date=today()):
	'''Get interest amount'''
	if not loan:
		return None
	posting_date = getdate(posting_date)
	billing_date = frappe.get_value('Loan', loan, 'billing_date') or posting_date.replace(day=1)
	start_date, end_date = get_interval(day_of_month=billing_date.day, date_obj=posting_date)
	paid_amount = frappe.db.sql("""
			SELECT sum(gl.credit - gl.debit)
			FROM `tabGL Entry` AS gl, `tabLoan` AS lt
			WHERE gl.against_voucher = lt.name
			AND gl.account = lt.interest_income_account
			AND gl.posting_date BETWEEN '{start_date}' AND '{end_date}'
			AND lt.name = '{loan}'
		""".format(loan=loan, start_date=start_date, end_date=end_date))[0][0] or 0
	principal = get_outstanding_principal(loan, posting_date)
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
