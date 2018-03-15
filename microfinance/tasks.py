import frappe
from frappe.utils.data import getdate, today


def daily():
    posting_date = today()
    generate_interest_receivable(posting_date)


def generate_interest_receivable(posting_date):
    loans = frappe.get_list('Loan', ['name', 'billing_date'], filters={
            'docstatus': 1,
            'recovery_status': ("in", "In Progress, Not Started"),
        })
    for loan_dict in loans:
        if getdate(loan_dict.get('billing_date')).day == \
                getdate(posting_date).day:
            loan = frappe.get_doc('Loan', loan_dict.get('name'))
            loan.convert_interest_to_principal(posting_date)
            # disable creating interest as receivable
            # loan.make_interest(posting_date, interest)
