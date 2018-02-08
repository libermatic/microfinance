# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from frappe.utils import getdate, add_months, get_datetime_str
from dateutil.relativedelta import relativedelta

def get_billing_date(current_date, billing_day=1):
    '''Return the next billing date from current_date'''
    date_obj = getdate(current_date)
    billing_date = date_obj.replace(day=billing_day)
    if billing_date <= date_obj:
        billing_date = add_months(billing_date, 1)
    return get_datetime_str(billing_date).split(' ')[0]

def month_diff(d1, d2):
    '''Return d1 - d2 in months without the days portion'''
    r = relativedelta(getdate(d1), getdate(d2))
    return r.years * 12 + r.months
