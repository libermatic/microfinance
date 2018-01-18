import frappe
from frappe.utils.data import getdate, today

def daily():
    generate_interest_receivable()

def generate_interest_receivable():
	loans = frappe.get_list('Loan', ['name', 'billing_date'], filters={
			'docstatus': 1,
			'recovery_status': 'In Progress',
		})
	for loan_dict in loans:
		if getdate(loan_dict.get('billing_date')).day == today().day:
			loan = frappe.get_doc('Loan', loan_dict.get('name'))
			loan.make_interest(today())
