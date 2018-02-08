# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def calculate_principal_and_duration(*args, **kwargs):
    from microfinance.microfinance_loan.api.calculate_principal_and_duration \
        import execute
    return execute(*args, **kwargs) 
