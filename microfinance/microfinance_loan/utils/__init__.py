# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from frappe.utils import getdate, add_months, get_datetime_str, flt
from dateutil.relativedelta import relativedelta
import math

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

def interest(amount, rate=0, slab=0):
    '''
        Return slabbed interest

        :param amount: Amount for which interest is to be calculated
        :param rate: Rate of interest in %
        :param slab: Discrete steps of amount on which insterest is calculated
    '''
    if slab:
        return (math.ceil(flt(amount) / slab) * slab) * rate / 100.0
    return amount * rate / 100.0
