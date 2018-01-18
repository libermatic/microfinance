# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import today, getdate, add_months, get_first_day, get_last_day
from datetime import date

from microfinance.microfinance_loan.doctype.loan.loan_utils import get_interval
from microfinance.microfinance_loan.doctype.loan.loan import get_billing_periods, get_outstanding_principal

durations = {
	'Last 3 Months': 4,
	'Last 6 Months': 7,
}

def execute(filters=None):
	period_list = get_periods(today(), durations.get(filters.get('duration')) or 1)
	columns = get_columns(period_list)
	data = get_data(period_list, filters=filters)
	return columns, data

def get_columns(period_list):
	columns = [
			{
				'fieldname': 'customer',
				'label': _("Customer"),
				'fieldtype': 'Link',
				'options': 'Customer',
				'width': 180,
			}, {
				'fieldname': 'loan',
				'label': _("Loan ID"),
				'fieldtype': 'Link',
				'options': 'Loan',
				'width': 90,
			}, {
				'fieldname': 'outstanding',
				'label': _("Outstanding"),
				'fieldtype': 'Currency',
				'options': 'currency',
				'width': 90,
			}
		]
	for period in period_list:
		columns.append({
				'fieldname': period.key,
				'label': period.label,
				'fieldtype': 'Currency',
				'options': 'currency',
				'width': 90,
			})
	columns.append({
			'fieldname': 'current_owed',
			'label': _("Current Owed"),
			'fieldtype': 'Currency',
			'options': 'currency',
			'width': 90,
		})
	return columns

def get_periods(period_date, no_of_periods=3):
	if not isinstance(period_date, date):
		period_date = getdate(period_date)
	periods = []
	for x in range(-no_of_periods + 1, 1):
		pd = add_months(period_date, x)
		periods.append(frappe._dict({
				'start_date': get_first_day(pd),
				'end_date': get_last_day(pd),
				'label': pd.strftime("%b %Y"),
				'key': pd.strftime("%b_%Y").lower(),
			}))
	return periods

def get_data(period_list, filters=None):
	show_npas_only = filters.get('show_npas_only')
	loan_plan = filters.get('loan_plan')
	loan_filters = {
		'docstatus': 1,
		'recovery_status': 'In Progress',
	}
	if loan_plan:
		loan_filters.update({ 'loan_plan': loan_plan })
	loans = frappe.get_list('Loan', [
			'name',
			'customer',
			'billing_date',
			'interest_receivable_account',
			'loan_account',
		], filters=loan_filters)
	data = []
	for loan in loans:
		row = [loan.customer, loan.name, get_outstanding_principal(loan.name)]
		total = 0
		for period in period_list:
			_0, _0, as_text = get_interval(
					getdate(loan.billing_date).day,
					period.start_date
				)
			conds = [
					"against = '{}'".format(as_text),
					"account = '{}'".format(loan.interest_receivable_account),
					"against_voucher_type = 'Loan'",
					"against_voucher = '{}'".format(loan.name),
				]
			owed = frappe.db.sql("""
				SELECT sum(debit) FROM `tabGL Entry` WHERE {}
			""".format(" AND ".join(conds)))[0][0] or 0
			conds = [
					"against = '{}'".format(as_text),
					"account = '{}'".format(loan.interest_receivable_account),
					"voucher_type = 'Loan'",
					"voucher_no = '{}'".format(loan.name),
				]
			converted = frappe.db.sql("""
				SELECT sum(credit) FROM `tabGL Entry` WHERE {}
			""".format(" AND ".join(conds)))[0][0] or 0
			amount = owed - converted
			total += amount
			row.append(amount)
		current_periods = get_billing_periods(loan.name, today(), 1)
		current_owed = 0
		if len(current_periods) == 1:
			current_owed = current_periods[0].get('interest')
		row.append(current_owed)
		if not show_npas_only:
			data.append(row)
		elif total == 0:
			data.append(row)
	return data
