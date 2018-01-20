# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest
from datetime import date
from frappe.utils.data import getdate

from microfinance.microfinance_loan.doctype.loan.loan_utils \
    import get_interval, get_periods

class TestLoanUtils(unittest.TestCase):
    def test_get_interval(self):
        '''Test get_interval correct returns'''
        self.assertEqual(
                get_interval(5, '2017-12-12'),
                (getdate('2017-12-05'), getdate('2018-01-04'), '2017-12-05 - 2018-01-04')
            )
        self.assertEqual(
                get_interval(12, '2017-12-05'),
                (getdate('2017-11-12'), getdate('2017-12-11'), '2017-11-12 - 2017-12-11')
            )
        self.assertEqual(
                get_interval(5, date(year=2017, month=12, day=12)),
                (getdate('2017-12-05'), getdate('2018-01-04'), '2017-12-05 - 2018-01-04')
            )
    def test_get_interval_known_edges(self):
        '''Test get_interval for known edge cases'''
        self.assertEqual(
                get_interval(5, '2017-12-31'),
                (getdate('2017-12-05'), getdate('2018-01-04'), '2017-12-05 - 2018-01-04')
            )
    def test_get_interval_for_end_of_the_month(self):
        '''Test get_periods for billing dates falling in end of the month'''
        self.assertEqual(
                get_interval(31, '2017-11-12'),
                (getdate('2017-10-31'), getdate('2017-11-29'), '2017-10-31 - 2017-11-29')
            )
        self.assertEqual(
                get_interval(31, '2018-02-12'),
                (getdate('2018-01-31'), getdate('2018-02-27'), '2018-01-31 - 2018-02-27')
            )
        self.assertEqual(
                get_interval(30, '2018-02-12'),
                (getdate('2018-01-30'), getdate('2018-02-27'), '2018-01-30 - 2018-02-27')
            )
    def test_get_interval_for_beginning_of_month(self):
        '''Test get_periods for billing dates falling in start of the month'''
        self.assertEqual(
                get_interval(1, '2017-09-01'),
                (getdate('2017-09-01'), getdate('2017-09-30'), '2017-09-01 - 2017-09-30')
            )

    def test_get_periods(self):
        '''Test get_periods correct returns'''
        actual = get_periods(5, '2017-12-12')
        expected = [
                { 'start_date': getdate('2017-09-05'), 'end_date': getdate('2017-10-04'), 'as_text': '2017-09-05 - 2017-10-04' },
                { 'start_date': getdate('2017-10-05'), 'end_date': getdate('2017-11-04'), 'as_text': '2017-10-05 - 2017-11-04' },
                { 'start_date': getdate('2017-11-05'), 'end_date': getdate('2017-12-04'), 'as_text': '2017-11-05 - 2017-12-04' },
                { 'start_date': getdate('2017-12-05'), 'end_date': getdate('2018-01-04'), 'as_text': '2017-12-05 - 2018-01-04' },
                { 'start_date': getdate('2018-01-05'), 'end_date': getdate('2018-02-04'), 'as_text': '2018-01-05 - 2018-02-04' },
            ]
        self.assertEqual(actual, expected)
    def test_get_periods_no_of_items(self):
        '''Test get_periods returns correct number of items'''
        actual = len(get_periods(5, '2017-12-12', 10))
        expected = 10
        self.assertEqual(actual, expected)
    def test_get_periods_billing_date_as_month_start(self):
        '''Test get_periods for billing dates falling in start of the month'''
        actual = get_periods(1, '2018-02-14', 3)
        expected =  [
                { 'start_date': getdate('2017-12-01'), 'end_date': getdate('2017-12-31'), 'as_text': '2017-12-01 - 2017-12-31' },
                { 'start_date': getdate('2018-01-01'), 'end_date': getdate('2018-01-31'), 'as_text': '2018-01-01 - 2018-01-31' },
                { 'start_date': getdate('2018-02-01'), 'end_date': getdate('2018-02-28'), 'as_text': '2018-02-01 - 2018-02-28' },
            ]
        self.assertEqual(actual, expected)
    def test_get_periods_billing_date_as_month_end(self):
        '''Test get_periods for billing dates falling in end of the month'''
        actual = get_periods(31, '2018-01-14', 5)
        expected =  [
                { 'start_date': getdate('2017-09-30'), 'end_date': getdate('2017-10-30'), 'as_text': '2017-09-30 - 2017-10-30' },
                { 'start_date': getdate('2017-10-31'), 'end_date': getdate('2017-11-29'), 'as_text': '2017-10-31 - 2017-11-29' },
                { 'start_date': getdate('2017-11-30'), 'end_date': getdate('2017-12-30'), 'as_text': '2017-11-30 - 2017-12-30' },
                { 'start_date': getdate('2017-12-31'), 'end_date': getdate('2018-01-30'), 'as_text': '2017-12-31 - 2018-01-30' },
                { 'start_date': getdate('2018-01-31'), 'end_date': getdate('2018-02-27'), 'as_text': '2018-01-31 - 2018-02-27' },
            ]
        self.assertEqual(actual, expected)
