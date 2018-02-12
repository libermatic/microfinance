# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today, add_months, cint, getdate

from microfinance.microfinance_loan.doctype.loan.loan \
	import get_interest, get_outstanding_principal
from microfinance.microfinance_loan.doctype.loan.loan_utils \
	import get_interval

def execute(filters=None):
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
			}, {
				'fieldname': 'status',
				'label': _("Status"),
				'fieldtype': 'Data',
				'width': 90,
			}, {
				'fieldname': 'last_posting_date',
				'label': _("Last Payment Date"),
				'fieldtype': 'Date',
				'width': 90,
			}, {
				'fieldname': 'last_billing_period',
				'label': _("Last Billing Period"),
				'fieldtype': 'Data',
				'width': 150,
			}, {
				'fieldname': 'outstanding',
				'label': _("Outstanding"),
				'fieldtype': 'Currency',
				'options': 'currency',
				'width': 90,
			}, {
				'fieldname': 'current_due',
				'label': _("Current Due"),
				'fieldtype': 'Currency',
				'options': 'currency',
				'width': 90,
			}
		]

	conds = [
			"loan.docstatus = 1",
			"loan.disbursement_status != 'Sanctioned'",
		]

	if filters.get('customer'):
		conds.append("loan.customer = '{}'".format(filters.get('customer')))
	if filters.get('loan'):
		conds.append("loan.name = '{}'".format(filters.get('loan')))
	if filters.get('display') == 'All Loans':
		conds.append("loan.recovery_status != 'Cancelled'")
	else:
		conds.append("loan.recovery_status in ('Not Started', 'In Progress')")

	result = frappe.db.sql('''
			SELECT
				max(gl.posting_date) AS posting_date,
				max(gl.period) AS period,
				loan.name as name,
				loan.recovery_status as recovery_status,
				loan.customer AS customer,
				loan.posting_date as loan_start_date,
				loan.billing_date as billing_date
			FROM
				`tabLoan`AS loan
			LEFT JOIN `tabGL Entry` AS gl
				ON gl.against_voucher = loan.name
				AND gl.voucher_type = 'Recovery'
			WHERE {}
			GROUP BY loan.name
		'''.format(" AND ".join(conds)), as_dict=True)
	data = []
	for loan in result:
		if filters.get('display') == 'NPA Only':
			npa_duration = frappe.get_value('Loan Settings', None, 'npa_duration')
			npa_date = add_months(today(), -cint(npa_duration))
			if loan.loan_start_date > getdate(npa_date):
				continue
			if loan.period:
				end_date = loan.period.split(' - ')[1]
				if getdate(end_date) > getdate(npa_date):
					continue
		start_date, end_date, _0 = get_interval(loan.billing_date.day, today())
		row = [
				loan.customer,
				loan.name,
				loan.recovery_status,
				loan.posting_date,
				loan.period,
				get_outstanding_principal(loan.name),
				get_interest(loan.name, start_date, end_date)
			]
		data.append(row)
	return columns, data
