# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"items": [
				{
					"type": "doctype",
					"name": "Loan Application",
					"description": _("Loans applied for"),
				},
				{
					"type": "doctype",
					"name": "Loan",
					"description": _("Customer loans"),
				},
			]
			},
		{
			"label": _("Transactions"),
			"items": [
				{
					"type": "doctype",
					"name": "Disbursement",
					"description": _("Loan payout to customers"),
				},
				{
					"type": "doctype",
					"name": "Recovery",
					"description": _("Loan payments received from customers"),
				},
			]
		},
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Loan Summary",
					"doctype": "Loan Summary",
				},
			]
		},
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Customers"),
				},
				{
					"type": "doctype",
					"name": "Loan Plan",
					"description": _("Types of loans"),
				},
				{
					"type": "doctype",
					"name": "Loan Settings",
					"description": _("Global loan configuration"),
				},
			]
		},
	]
