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
					"name": "Customer",
					"description": _("Customers"),
				},
                {
                "type": "doctype",
                "name": "Loan",
                "description": _("Customer loans"),
                },
				{
					"type": "doctype",
					"name": "Loan Plan",
					"description": _("Types of loans"),
				},
			]
		},
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Loan Settings",
					"description": _("Global loan configuration"),
				},
			]
		},
	]
