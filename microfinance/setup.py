# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.exceptions import DuplicateEntryError

def _create_account(doc, company_name, company_abbr):
	account = frappe.get_doc({
			'doctype': 'Account',
			'account_name': doc['account_name'],
			'parent_account': "{} - {}".format(doc['parent_account'], company_abbr),
			'is_group': 0,
			'company': company_name,
			'account_type': doc.get('account_type'),
		}).insert(ignore_if_duplicate=True)
	return account.name

loan_settings_accounts = {
	'loan_account': {
			'account_name': 'Microfinance Loans',
			'parent_account': 'Loans and Advances (Assets)',
		},
	'interest_income_account': {
			'account_name': 'Interests on Loans',
			'parent_account': 'Indirect Income',
		},
	'interest_receivable_account': {
			'account_name': 'Interests Receivable',
			'parent_account': 'Accounts Receivable',
		}
}

def after_wizard_complete(args=None):
	'''
	Create new accounts and set Loan Settings.
	'''
	if frappe.defaults.get_global_default('country') != "India":
		return
	loan_settings = frappe.get_doc('Loan Settings', None)
	loan_settings.update({
			'mode_of_payment' : 'Cash',
			'cost_center': frappe.db.get_value('Company', args.get('company_name'), 'cost_center')
		})
	for key, value in loan_settings_accounts.items():
		account_name = _create_account(
				value,
				args.get('company_name'),
				args.get('company_abbr')
			)
		loan_settings.update({ key: account_name })
	loan_settings.save()
