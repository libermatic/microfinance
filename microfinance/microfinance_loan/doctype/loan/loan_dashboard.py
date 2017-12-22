from frappe import _

def get_data():
	return {
		'fieldname': 'loan',
		'non_standard_fieldnames': {
			'Journal Entry': 'reference_name',
			},
		'transactions': [
			{
				'label': _('Account'),
				'items': ['Journal Entry', 'Disbursement', 'Recovery']
			}
		]
	}
