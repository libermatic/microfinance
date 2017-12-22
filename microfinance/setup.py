# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.exceptions import DuplicateEntryError

def _create_account(doc, company_name):
	abbr = frappe.get_value('Company', company_name, 'abbr')
	return frappe.get_doc({
			'doctype': "Account",
			'account_name': doc['account_name'],
			'parent_account': "{} - {}".format(doc['parent_account'], abbr),
			'is_group': 0,
			'company': company_name,
			'account_type': doc.get('account_type'),
		}).insert(ignore_if_duplicate=True)

def _set_fixtures():
	options = frappe.get_meta('Journal Entry Account').get_field('reference_type').options
	if not '\nLoan' in :
		doc = frappe.new_doc('Property Setter')
		value = options + '\nLoan'
		doc.update({
				'doc_type': 'Journal Entry Account',
				'field_name' :'reference_type',
				'property': 'options',
				'property_type': 'Text',
				'value': value
			})
		doc.insert(ignore_permissions=True)

def after_wizard_complete(args=None):
	if frappe.defaults.get_global_default('country') != "India":
		return

	company_name = frappe.defaults.get_global_default('company')

	_create_account({
			'account_name': "Microfinance Loans",
			'parent_account': "Loans and Advances (Assets)",
		}, company_name)

	_create_account({
			'account_name': "Interests on Loans",
			'parent_account': "Indirect Income",
		}, company_name)

	_set_fixtures()
