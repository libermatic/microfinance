# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from microfinance.microfinance_loan.doctype.loan.test_loan import create_loan

class TestDisbursement(unittest.TestCase):
	pass

def make_disbursement(**args):
	disbursement = frappe.new_doc("Disbursement")
	args = frappe._dict(args)
	if args.posting_date:
		disbursement.posting_date = args.posting_date
	if args.loan:
		disbursement.loan = args.loan

	if not args.do_not_save:
		disbursement.insert()
		if not args.do_not_submit:
			disbursement.submit()

	return disbursement
