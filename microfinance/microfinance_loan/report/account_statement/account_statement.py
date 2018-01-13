# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import reduce
from frappe.utils import flt

def make_row(result):
	row = [
		result.get('posting_date'),
		result.get('account'),
		result.get('credit'),
		result.get('debit'),
		result.get('amount'),
		result.get('remarks')
		]
	return row

def execute(filters=None):
	columns = [
			_("Posting Date") + ":Date:90",
			_("Account") + ":Link/Account:160",
			_("Credit") + ":Currency/currency:90",
			_("Debit") + ":Currency/currency:90",
			_("Amount") + ":Currency/currency:90",
			_("Remarks") + "::300",
		]

	loan_name = filters.get('loan')
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	excluded_accounts = frappe.db.get_value(
			'Loan',
			loan_name,
			['loan_account', 'interest_receivable_account']
		)

	conds = [
			"against_voucher_type = 'Loan'",
			"against_voucher = '{}'".format(loan_name),
			"account NOT IN ({})".format(', '.join(map(lambda x: "'{}'".format(x), excluded_accounts)))
		]

	opening = frappe.db.sql("""
			SELECT
				sum(credit) AS credit,
				sum(debit) AS debit,
				sum(credit - debit) as amount
			FROM `tabGL Entry` AS GL
			WHERE {conds} AND posting_date < '{from_date}'
		""".format(conds=" AND ".join(conds), from_date=from_date), as_dict=True)

	opening_credit = flt(opening[0].get('credit'))
	opening_debit = flt(opening[0].get('debit'))
	opening_amount = flt(opening[0].get('amount'))

	data = [
		[None, _("Opening"), opening_credit, opening_debit, opening_amount, None]
	]

	results = frappe.db.sql("""
			SELECT
				account,
				posting_date,
				sum(credit) as credit,
				sum(debit) as debit,
				sum(credit - debit) AS amount,
				remarks
			FROM `tabGL Entry` AS remarks
			WHERE {conds}
			AND posting_date BETWEEN '{from_date}' AND '{to_date}'
			GROUP BY voucher_type, voucher_no, account, remarks
			ORDER BY name
		""".format(
				conds=" AND ".join(conds),
				from_date=from_date,
				to_date=to_date
			), as_dict=True)
	for result in results:
		row = make_row(result)
		if row:
			data.append(row)

	total_credit = reduce((lambda a, x: a + x.get('credit')), results, 0)
	total_debit = reduce((lambda a, x: a + x.get('debit')), results, 0)
	total_amount = reduce((lambda a, x: a + x.get('amount')), results, 0)

	data.append([None, _("Total"), total_credit, total_debit, total_amount, None])
	data.append([
			None,
			_("Closing"),
			opening_credit + total_credit,
			opening_debit + total_debit,
			opening_amount + total_amount,
			None
		])

	return columns, data
