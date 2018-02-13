# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and Contributors
# See license.txt

from __future__ import unicode_literals
import unittest
import frappe

from microfinance.microfinance_loan.utils \
    import get_billing_date, month_diff, interest

class TestUtils(unittest.TestCase):

    def test_get_billing_date(self):
        '''Test get_billing_date default case'''
        actual = get_billing_date('2017-12-12')
        expected = '2018-01-01'
        self.assertEqual(actual, expected)
    def test_get_billing_date_before(self):
        '''Test get_billing_date when billing_day is before current_date day'''
        actual = get_billing_date('2017-12-12', 27)
        expected = '2017-12-27'
        self.assertEqual(actual, expected)
    def test_get_billing_date_same(self):
        '''Test get_billing_date when billing_day is equal to current_date day'''
        actual = get_billing_date('2017-12-12', 12)
        expected = '2018-01-12'
        self.assertEqual(actual, expected)
    def test_get_billing_date_after(self):
        '''Test get_billing_date when billing_day is after current_date day'''
        actual = get_billing_date('2017-12-12', 5)
        expected = '2018-01-05'
        self.assertEqual(actual, expected)

    def test_month_diff(self):
        '''Test month_diff default case'''
        actual = month_diff('2020-08-19', '2017-12-12')
        expected = 32
        self.assertEqual(actual, expected)
    def test_month_diff_same_day(self):
        '''Test month_diff when the day of the month is the same'''
        actual = month_diff('2020-08-12', '2017-12-12')
        expected = 32
        self.assertEqual(actual, expected)
    def test_month_diff_feb_leap(self):
        '''Test month_diff when the other day is Feb 29'''
        actual = month_diff('2020-02-29', '2018-02-28')
        expected = 24
        self.assertEqual(actual, expected)

    def test_interest(self):
        '''Test interest default case'''
        actual = interest(92000)
        expected = 0
        self.assertEqual(actual, expected)
    def test_interest_with_rate(self):
        '''Test interest with rate'''
        actual = interest(92000, 5)
        expected = 4600
        self.assertEqual(actual, expected)
    def test_interest_with_slab(self):
        '''Test interest with slab'''
        actual = interest(92000, 5, 10000)
        expected = 5000
        self.assertEqual(actual, expected)
