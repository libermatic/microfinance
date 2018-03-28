# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, today, add_days
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.utils.data import fmt_money

from microfinance.microfinance_loan.doctype.loan.loan \
    import get_outstanding_principal, get_interest
from microfinance.microfinance_loan.doctype.loan.loan_utils \
    import billed_interest, converted_interest
from microfinance.microfinance_loan.utils import humanify_period


class Recovery(AccountsController):
    def validate(self):
        outstanding_principal = get_outstanding_principal(
            self.loan, self.posting_date
        )
        if self.amount > outstanding_principal + flt(self.interest):
            frappe.throw(_(
                "Cannot recover more that the outstanding principal: \
                    {}".format(outstanding_principal)
            ))
        if self.interest > 0:
            converted = converted_interest(self.loan, self.billing_period)
            if converted > 0:
                frappe.throw(_(
                    "Interest for period {} has already been converted to \
                        principal".format(humanify_period(self.billing_period))
                ))

    def before_save(self):
        if not self.interest:
            self.billing_period = None

    def on_submit(self):
        self.make_gl_entries()
        update_loan_status(self.loan, posting_date=self.posting_date)

    def on_cancel(self):
        self.make_gl_entries(cancel=True)
        update_loan_status(self.loan, posting_date=self.posting_date)

    def make_gl_entries(self, cancel=0, adv_adj=0):
        gl_entries = []

        if self.billing_period:
            unbilled = self.get_unbilled()
            if unbilled:
                self.add_billing_gl_entries(gl_entries, unbilled)
        if self.interest:
            self.add_party_gl_entries(gl_entries)
        if self.principal:
            self.add_loan_gl_entries(gl_entries)
        if len(self.loan_charges) > 0:
            self.add_charges_gl_entries(gl_entries)

        make_gl_entries(
            gl_entries,
            cancel=cancel,
            adv_adj=adv_adj,
            merge_entries=False
        )

    def get_gl_dict(self, args):
        gl_dict = frappe._dict({
                'against_voucher_type': 'Loan',
                'against_voucher': self.loan
            })
        gl_dict.update(args)
        gle = super(Recovery, self).get_gl_dict(gl_dict)
        if args.get('posting_date'):
            gle.update({ 'posting_date': args.get('posting_date') })
        return gle

    def get_unbilled(self):
        start_date, end_date = self.billing_period.split(' - ')
        actual = get_interest(
            self.loan,
            end_date=add_days(end_date, 1),
            actual=True
        )
        billed = billed_interest(self.loan, self.billing_period)
        unbilled = 0.0
        if actual > billed:
            unbilled = unbilled + actual - billed
        if self.interest > actual:
            unbilled = unbilled + self.interest - actual
        return unbilled

    def add_billing_gl_entries(self, gl_entries, unbilled):
        posting_date = add_days(self.billing_period.split(' - ')[1], 1)
        gl_entries.append(
                self.get_gl_dict({
                        'posting_date':posting_date,
                        'account': self.interest_income_account,
                        'credit': unbilled,
                        'cost_center': frappe.db.get_value(
                            'Loan Settings',
                            None,
                            'cost_center'
                        ),
                        'against': self.customer,
                        'remarks': 'Interest for period: {}'.format(
                            humanify_period(self.billing_period)
                        )
                    })
            )
        gl_entries.append(
                self.get_gl_dict({
                        'posting_date':posting_date,
                        'account': self.interest_receivable_account,
                        'debit': unbilled,
                        'party_type': 'Customer',
                        'party': self.customer,
                        'against': self.interest_income_account,
                        'period': self.billing_period,
                    })
            )

    def add_party_gl_entries(self, gl_entries):
        gl_entries.append(
                self.get_gl_dict({
                        'account': self.payment_account,
                        'debit': self.interest,
                        'against': self.customer,
                        'remarks': make_remarks(self.principal)
                    })
            )
        gl_entries.append(
                self.get_gl_dict({
                        'account': self.interest_receivable_account,
                        'credit': self.interest,
                        'party_type': 'Customer',
                        'party': self.customer,
                        'against': self.payment_account,
                        'period': self.billing_period,
                    })
            )

    def add_loan_gl_entries(self, gl_entries):
        gl_entries.append(
                self.get_gl_dict({
                        'account': self.loan_account,
                        'credit': self.principal,
                        'against': self.payment_account,
                    })
            )
        gl_entries.append(
                self.get_gl_dict({
                        'account': self.payment_account,
                        'debit': self.principal,
                        'against': self.customer,
                        'remarks': make_remarks(self.principal)
                    })
            )

    def add_charges_gl_entries(self, gl_entries):
        total = 0
        cost_center = frappe.db.get_value('Loan Settings', None, 'cost_center')
        for row in self.loan_charges:
            total += row.charge_amount
            gl_entries.append(
                    self.get_gl_dict({
                            'account': row.charge_account,
                            'credit': row.charge_amount,
                            'cost_center': cost_center,
                            'remarks': row.charge
                        })
                )
        gl_entries.append(
                self.get_gl_dict({
                        'account': self.payment_account,
                        'debit': total,
                        'against': self.customer,
                    })
            )


def make_remarks(principal=None):
    remarks = 'Payment received'
    if principal:
        remarks += '. Capital: {}'.format(fmt_money(
                principal,
                precision=0,
                currency=frappe.defaults.get_user_default('currency')
            ))
    return remarks


def update_loan_status(loan_name, posting_date=today()):
    '''Method update recovery_status of Loan'''
    disbursement_status, loan_principal, recovery_status = frappe.get_value(
            'Loan',
            loan_name,
            ['disbursement_status', 'loan_principal', 'recovery_status']
        )
    outstanding_principal = get_outstanding_principal(loan_name)
    loan = frappe.get_doc('Loan', loan_name)
    do_save = False
    if disbursement_status == 'Fully Disbursed' and outstanding_principal == 0:
        loan.clear_date = posting_date
        loan.recovery_status = 'Repaid'
        do_save = True
    else:
        if outstanding_principal == loan_principal \
                and recovery_status != 'Not Started':
            loan.recovery_status = 'Not Started'
            do_save = True
        elif recovery_status != 'In Progress':
            loan.recovery_status = 'In Progress'
            do_save = True
        if loan.clear_date:
            loan.clear_date = None
            do_save = True
    if do_save:
        return loan.save()
    return None
