import frappe
from frappe import _

from microfinance.microfinance_loan.doctype.loan.loan \
    import get_undisbursed_principal, get_outstanding_principal, \
    get_recovered_principal, get_wrote_off_principal


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
                'label': _('Adjustment'),
                'items': ['Loan Write Off']
            }
        ]
    }


@frappe.whitelist()
def get_loan_chart_data(docname):
    recovered = get_recovered_principal(docname)
    outstanding = get_outstanding_principal(docname)
    undisbursed = get_undisbursed_principal(docname)
    wrote_off = get_wrote_off_principal(docname)

    data = {
        'labels': [
                'Recovered', 'Outstanding', 'Undisbursed', 'Wrote Off'
            ],
        'datasets': [
            {
                'title': "Total",
                'values': [recovered, outstanding, undisbursed, wrote_off]
            },
        ]
    }
    return data
