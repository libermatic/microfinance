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
		'recovery_status': ("in", "In Progress, Not Started"),
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

	def get_amount(entries, interval, key='amount'):
		start_date, end_date, _0 = interval
		amount = 0
		for entry in entries:
			entry_date = getdate(entry.get('period').split(' - ')[0])
			if start_date <= entry_date < end_date:
				amount += entry.get(key)
		return amount

	column_total_dict = {}
	def update_column_total(key, value):
		prev_value = column_total_dict.get(key) or 0
		column_total_dict.update({ key: prev_value + value })

	for loan in loans:
		outstanding = get_outstanding_principal(loan.name)
		update_column_total('outstanding', outstanding)
		row = [loan.customer, loan.name, outstanding]
		total = 0

		# this will be the list of entries that could be entered by Recovery or
		# Loan scheduled tasks
		owed_entries = frappe.db.sql("""
				SELECT period, sum(debit) as amount, sum(credit) as paid_amount
				FROM `tabGL Entry`
				WHERE account = '{0}'
				AND (
						(voucher_type = 'Loan' AND voucher_no = '{1}') OR
						(against_voucher_type = 'Loan' AND against_voucher = '{1}')
					)
				GROUP BY period
			""".format(
				loan.interest_receivable_account,
				loan.name
			), as_dict=True)

		# this will be the list of entries that has been converted to principal
		# by Loan scheduled tasks
		converted_entries = frappe.db.sql("""
				SELECT period, sum(debit) as amount
				FROM `tabGL Entry`
				WHERE account = '{0}'
				AND voucher_type = 'Loan' AND voucher_no = '{1}' AND period IS NOT NULL
				GROUP BY period
			""".format(
				loan.loan_account,
				loan.name
			), as_dict=True)

		for period in period_list:
			interval = get_interval(getdate(loan.billing_date).day, period.start_date)
			converted_entry = get_amount(converted_entries, interval)
			paid_amount = get_amount(owed_entries, interval, 'paid_amount')
			amount = 0
			if converted_entry == 0 and paid_amount > 0:
				amount = get_amount(owed_entries, interval)
			total += amount
			update_column_total(period.key, amount)
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

	total_row = [_("Total"), None, column_total_dict.get('outstanding')]
	for period in period_list:
		column_total = column_total_dict.get(period.key) or 0
		total_row.append(column_total)
	data.append(total_row)

	return data
