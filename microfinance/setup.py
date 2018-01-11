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
		}
}

def after_wizard_complete(args=None):
	if frappe.defaults.get_global_default('country') != "India":
		return
	loan_settings = frappe.get_doc('Loan Settings', None)
	loan_settings.update({ 'mode_of_payment' : 'Cash' })
	for key, value in loan_settings_accounts.items():
		account_name = _create_account(
				value,
				args.get('company_name'),
				args.get('company_abbr')
			)
		loan_settings.update({ key: account_name })
	loan_settings.save()

def _set_fixtures():
	options = frappe.get_meta('Journal Entry Account').get_field('reference_type').options
    # for property setter
	if not '\nLoan' in options:
		doc = frappe.new_doc('Property Setter')
		value = options + '\nLoan'
		doc.update({
				'doc_type': 'Journal Entry Account',
				'doctype_or_field': 'DocField',
				'field_name' :'reference_type',
				'property': 'options',
				'property_type': 'Text',
				'value': value
			})
		doc.insert(ignore_permissions=True)

    # for custom field
	frappe.get_doc({
			'doctype': 'Custom Field',
			'dt': 'Journal Entry Account',
			'label': 'Transaction Details',
			'fieldname': 'transaction_details',
			'insert_after': 'against_account',
			'fieldtype': 'Text',
		}).insert(ignore_if_duplicate=True)

def after_install(args=None):
	_set_fixtures()
