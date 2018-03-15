# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def _create_account(doc, company_name, company_abbr):
    account = frappe.get_doc({
            'doctype': 'Account',
            'account_name': doc['account_name'],
            'parent_account': "{} - {}".format(
                doc['parent_account'], company_abbr
            ),
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
            'mode_of_payment': 'Cash',
            'cost_center': frappe.db.get_value(
                'Company', args.get('company_name'), 'cost_center'
            )
        })
    for key, value in loan_settings_accounts.items():
        account_name = _create_account(
                value,
                args.get('company_name'),
                args.get('company_abbr')
            )
        loan_settings.update({key: account_name})
    loan_settings.save()


def _set_fixtures():
    # for custom field
    frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'GL Entry',
            'label': 'Period',
            'fieldname': 'period',
            'insert_after': 'fiscal_year',
            'fieldtype': 'Text',
        }).insert(ignore_if_duplicate=True)

    frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Customer',
            'label': 'Loanee Details',
            'fieldname': 'loanee_details',
            'insert_after': 'email_id',
            'fieldtype': 'Section Break',
            'depends_on': 'eval:doc.__unsaved!=1',
        }).insert(ignore_if_duplicate=True)

    frappe.get_doc({
            'doctype': 'Custom Field',
            'dt': 'Customer',
            'label': 'Loanee Details HTML',
            'fieldname': 'loanee_details_html',
            'insert_after': 'loanee_details',
            'fieldtype': 'HTML',
            'depends_on': 'eval:doc.__unsaved!=1',
            'read_only': 1,
        }).insert(ignore_if_duplicate=True)


def after_install(args=None):
    _set_fixtures()
