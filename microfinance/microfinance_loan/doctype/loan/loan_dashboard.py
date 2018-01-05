import frappe
from frappe import _

from microfinance.microfinance_loan.doctype.loan.loan \
	import get_undisbursed_principal, get_outstanding_principal, get_recovered_principal


def get_data(d=None):
	return {
		'fieldname': 'loan',
		'non_standard_fieldnames': {
				'Journal Entry': 'reference_name',
			},
		'transactions': [
			{
				'label': _('Payment'),
				'items': ['Disbursement', 'Recovery']
			},
			{
				'label': _('Account'),
				'items': ['Journal Entry']
			}
		]
	}

@frappe.whitelist()
def get_loan_chart_data(docname):
	recovered = get_recovered_principal(docname)
	outstanding = get_outstanding_principal(docname)
	undisbursed = get_undisbursed_principal(docname)

	data = {
		'labels': [
				'Recovered', 'Outstanding', 'Undisbursed'
			],
		'datasets': [
			{
				'title': "Total",
				'values': [recovered, outstanding, undisbursed]
			},
		]
	}
	return data
