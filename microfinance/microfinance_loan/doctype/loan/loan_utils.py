from datetime import date
from frappe.utils import cint
from frappe.utils.data import getdate, add_months, add_days, date_diff, get_last_day

def get_interval(day_of_month, date_obj):
	'''Returns start and end date of the interval'''
	if not isinstance(date_obj, date):
		date_obj = getdate(date_obj)
	try:
		start_date = date_obj.replace(day=day_of_month)
	except ValueError:
		start_date = add_months(date_obj, -1).replace(day=day_of_month)
	if date_diff(date_obj, start_date) < 0:
		start_date = add_months(start_date, -1)
	try:
		end_date = date_obj.replace(day=day_of_month)
	except ValueError:
		end_date = get_last_day(date_obj)
	if date_diff(end_date, date_obj) <= 0:
		end_date = add_months(end_date, 1)
	if end_date.day >= day_of_month:
		end_date = add_days(end_date, -1)
	return start_date, end_date

def get_periods(day_of_month, date_obj, no_of_periods=5):
	intervals = []
	limit_start = -((cint(no_of_periods) + 1) / 2) + 1
	limit_end = cint(no_of_periods) / 2 + 1
	for x in range(limit_start, limit_end):
		start_date, end_date = get_interval(day_of_month, add_months(date_obj, x))
		intervals.append({
				'start_date': start_date,
				'end_date': end_date
			})
	return intervals
