# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestLoan(unittest.TestCase):
	pass

def make_loan(**args):
	loan = frappe.new_doc("Loan")
	args = frappe._dict(args)
	if args.posting_date:
		loan.posting_date = args.posting_date

	loan.company = args.company or "_Test Company"
	loan.customer = args.customer or "_Test Customer"

	loan.loan_plan = args.loan_plan or "_Test Loan Plan"
	loan.loan_principal = args.loan_principal or 10000
	loan.rate_of_interest = args.rate_of_interest or 10
	if not args.do_not_save:
		loan.insert()
		if not args.do_not_submit:
			loan.submit()

	return loan
