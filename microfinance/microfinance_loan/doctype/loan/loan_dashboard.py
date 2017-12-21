from frappe import _

def get_data():
	return {
		'fieldname': 'customer',
		'non_standard_fieldnames': {
			'Journal Entry': 'reference_name',
			'Disbursement': 'name',
			'Recovery': 'name'
			},
		'transactions': [
			{
				'label': _('Account'),
				'items': ['Journal Entry', 'Disbursement', 'Recovery']
			}
		]
	}
