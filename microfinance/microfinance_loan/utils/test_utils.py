# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and Contributors
# See license.txt

from __future__ import unicode_literals
import unittest
import frappe

from microfinance.microfinance_loan.utils import get_billing_date

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
