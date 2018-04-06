# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
# from frappe.utils import flt, add_months, add_days, getdate, today
# from microfinance.microfinance_loan.utils \
#     import get_billing_date, month_diff, interest


@frappe.whitelist()
def list(loan):
    return ['lo']
