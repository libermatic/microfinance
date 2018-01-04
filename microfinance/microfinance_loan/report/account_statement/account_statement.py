# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import reduce
from frappe.utils import flt

description = {
		'disbursement': 'Disbursed',
		'recovery': 'recovered',
		'interest': 'inte',
		'interest_converted_to_principal': '',
		'processing_fees': '',
	}

def make_row(result, accounts):
	row = [
		result.get('posting_date'),
		result.get('transaction_details'),
		result.get('credit'),
		result.get('debit'),
		result.get('remarks')
		]
	return row

def execute(filters=None):
	columns = [
			_("Posting Date") + ":Date:90",
			_("Details") + "::160",
			_("Credit") + ":Currency/currency:90",
			_("Debit") + ":Currency/currency:90",
			_("Remarks") + "::400",
		]

	loan_name = filters.get('loan')
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	interest_income_account = frappe.db.get_value(
			'Loan',
			loan_name,
			'interest_income_account'
		)
	results = frappe.db.sql("""
			SELECT
				GL.posting_date AS posting_date,
				GL.account AS account,
				GL.against AS against,
				GL.credit AS credit,
				GL.debit AS debit,
				GL.voucher_no as voucher_no,
				Journal.transaction_details AS transaction_details,
				GL.remarks as remarks
			FROM
				`tabGL Entry` AS GL,
				`tabJournal Entry Account` AS Journal,
				`tabLoan` as Loan
			WHERE GL.voucher_no = Journal.parent
			AND GL.against_voucher='{loan}'
			AND Journal.account = GL.account
			AND Journal.against_account = GL.against
			AND GL.against_voucher_type='Loan'
			AND Loan.loan_account != GL.account
			AND Loan.name = GL.against_voucher
			AND GL.posting_date BETWEEN '{from_date}' AND '{to_date}'
		""".format(loan=loan_name, from_date=from_date, to_date=to_date), as_dict=True)
	opening = frappe.db.sql("""
			SELECT
				sum(GL.credit) AS credit,
				sum(GL.debit) AS debit
			FROM `tabGL Entry` AS GL,
					`tabLoan` as Loan
			WHERE GL.posting_date < '{from_date}'
			AND GL.against_voucher_type='Loan'
			AND GL.against_voucher='{loan}'
			AND Loan.loan_account != GL.account
			AND Loan.name = GL.against_voucher
		""".format(loan=loan_name, from_date=from_date), as_dict=True)
	opening_credit = flt(opening[0].get('credit'))
	opening_debit = flt(opening[0].get('debit'))
	data = [
		[None, _("Opening"), opening_credit, opening_debit, None]
	]
	accounts = {
			'payment_account': 'Cash - C',
			'interest_income_account': interest_income_account
		}
	for result in results:
		row = make_row(result, accounts)
		if row:
			data.append(row)

	total_credit = reduce((lambda a, x: a + x.get('credit')), results, 0)
	total_debit = reduce((lambda a, x: a + x.get('debit')), results, 0)
	data.append([None, _("Total"), total_credit, total_debit, None])
	data.append([None, _("Closing"), opening_credit + total_credit, opening_debit + total_debit, None])

	return columns, data
