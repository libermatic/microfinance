# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.utils.data import getdate

from microfinance.microfinance_loan.report.asset_performance.asset_performance \
    import get_periods

class TestAssetPerformace(unittest.TestCase):
    def test_get_periods(self):
        '''Test whether function returns expected results'''
        actual = get_periods('2017-12-12')
        expected = [
                { 'start_date': getdate('2017-10-01'), 'end_date': getdate('2017-10-31'), 'label': 'Oct 2017', 'key': 'oct_2017' },
                { 'start_date': getdate('2017-11-01'), 'end_date': getdate('2017-11-30'), 'label': 'Nov 2017', 'key': 'nov_2017' },
                { 'start_date': getdate('2017-12-01'), 'end_date': getdate('2017-12-31'), 'label': 'Dec 2017', 'key': 'dec_2017' },
            ]
        self.assertEqual(actual, expected)
    def test_get_periods_args_with_date_instance(self):
        '''Test function works with date objext as well'''
        actual = get_periods(getdate('2017-12-12'), 3)
        expected = [
                { 'start_date': getdate('2017-10-01'), 'end_date': getdate('2017-10-31'), 'label': 'Oct 2017', 'key': 'oct_2017' },
                { 'start_date': getdate('2017-11-01'), 'end_date': getdate('2017-11-30'), 'label': 'Nov 2017', 'key': 'nov_2017' },
                { 'start_date': getdate('2017-12-01'), 'end_date': getdate('2017-12-31'), 'label': 'Dec 2017', 'key': 'dec_2017' },
            ]
        self.assertEqual(actual, expected)
    def test_get_periods_spanning_different_years(self):
        '''Test when periods span mulitple years'''
        actual = get_periods('2018-04-30', 6)
        expected = [
                { 'start_date': getdate('2017-11-01'), 'end_date': getdate('2017-11-30'), 'label': 'Nov 2017', 'key': 'nov_2017' },
                { 'start_date': getdate('2017-12-01'), 'end_date': getdate('2017-12-31'), 'label': 'Dec 2017', 'key': 'dec_2017' },
                { 'start_date': getdate('2018-01-01'), 'end_date': getdate('2018-01-31'), 'label': 'Jan 2018', 'key': 'jan_2018' },
                { 'start_date': getdate('2018-02-01'), 'end_date': getdate('2018-02-28'), 'label': 'Feb 2018', 'key': 'feb_2018' },
                { 'start_date': getdate('2018-03-01'), 'end_date': getdate('2018-03-31'), 'label': 'Mar 2018', 'key': 'mar_2018' },
                { 'start_date': getdate('2018-04-01'), 'end_date': getdate('2018-04-30'), 'label': 'Apr 2018', 'key': 'apr_2018' },
            ]
        self.assertEqual(actual, expected)
