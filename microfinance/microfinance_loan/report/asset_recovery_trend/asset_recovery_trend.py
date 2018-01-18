# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from datetime import date

from frappe.utils.data import getdate, today, date_diff
from erpnext.accounts.report.financial_statements \
	import get_period_list, get_columns, get_data

from microfinance.microfinance_loan.doctype.loan.loan import get_outstanding_principal

def execute(filters=None):
	periodicity = filters.get('periodicity')
	period_list = get_period_list(
			filters.get('from_fiscal_year'),
			filters.get('to_fiscal_year'),
			filters.get('periodicity')
		)
	columns = get_columns(periodicity, period_list)
	data = get_data(periodicity, period_list)
	return columns, data

def get_columns(periodicity, period_list):
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
				'width': 120,
			}
		]
	for period in period_list:
		columns.append({
			'fieldname': period.key,
			'label': period.label,
			'fieldtype': 'Currency',
			'options': 'currency',
			'width': 150
		})
	if periodicity != 'Yearly':
		columns.append({
				'fieldname': 'total',
				'label': _("Total"),
				'fieldtype': 'Currency',
				'width': 150
			})
	return columns

def get_period_key(start_date, periodicity):
	if periodicity == 'Monthly':
		return date.strftime(start_date, '%b_%Y').lower()
	if periodicity == 'Quarterly':
		if start_date.month < 4:
			month = 'mar'
		elif start_date.month < 7:
			month = 'jun'
		elif start_date.month < 10:
			month = 'sep'
		else:
			month = 'dec'
		return '{}_{}'.format(month, start_date.year)
	if periodicity == 'Half-Yearly':
		if start_date.month < 4:
			key = 'mar_{}'.format(start_date.year)
		elif start_date.month < 10:
			key = 'sep_{}'.format(start_date.year)
		else:
			key = 'mar_{}'.format(start_date.year + 1)
		return key
	if periodicity == 'Yearly':
		return 'mar_{}'.format(start_date.year if start_date.month < 4 else start_date.year + 1)

def get_data(periodicity, period_list):
	loans = frappe.get_list('Loan', ['name', 'customer', 'loan_account'], filters = {
			'docstatus': 1,
			'recovery_status': 'In Progress',
		})
	data = []
	column_total_dict = {}
	for loan in loans:
		row = [loan.get('customer'), loan.get('name')]
		row_total = 0
		recovered = frappe.db.sql("""
				SELECT posting_date, sum(credit) AS amount
				FROM `tabGL Entry`
				WHERE account='{}' AND against_voucher='{}'
				GROUP BY posting_date
			""".format(loan.get('loan_account'), loan.get('name')), as_dict=True)
		recovered_dict = {}
		for r in recovered:
			key = get_period_key(r.get('posting_date'), periodicity)
			amount = recovered_dict.get(key) or 0
			amount += r.get('amount')
			recovered_dict.update({ key: amount })
		for period in period_list:
			row_total += recovered_dict.get(period.key) or 0

			column_total = column_total_dict.get(period.key) or 0
			column_total += recovered_dict.get(period.key) or 0
			column_total_dict.update({ period.key: column_total })

			row.append(recovered_dict.get(period.key))

		row.append(row_total)
		data.append(row)

	totals = [_("Total"), None]
	grand_total = 0
	for period in period_list:
		column_total = column_total_dict.get(period.key) or 0
		totals.append(column_total)

		grand_total += column_total
	totals.append(grand_total)
	data.append(totals)

	return data
