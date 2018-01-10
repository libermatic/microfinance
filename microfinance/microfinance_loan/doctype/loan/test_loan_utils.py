# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest
from datetime import date

from microfinance.microfinance_loan.doctype.loan.loan import get_interval

class TestLoanUtils(unittest.TestCase):
    def test_get_interval(self):
        '''Test correct returns'''
        self.assertEqual(
                get_interval(5, '2017-12-12'),
                (date(year=2017, month=12, day=5), date(year=2018, month=1, day=4))
            )
        self.assertEqual(
                get_interval(12, '2017-12-05'),
                (date(year=2017, month=11, day=12), date(year=2017, month=12, day=11))
            )
        self.assertEqual(
                get_interval(5, date(year=2017, month=12, day=12)),
                (date(year=2017, month=12, day=5), date(year=2018, month=1, day=4))
            )
    def test_get_interval_known_edges(self):
        '''Test for known edge cases'''
        self.assertEqual(
                get_interval(5, '2017-12-31'),
                (date(year=2017, month=12, day=5), date(year=2018, month=1, day=4))
            )
        self.assertEqual(
                get_interval(31, '2017-11-12'),
                (date(year=2017, month=10, day=31), date(year=2017, month=11, day=30))
            )
        self.assertEqual(
                get_interval(31, '2018-02-12'),
                (date(year=2018, month=1, day=31), date(year=2018, month=2, day=28))
            )
        self.assertEqual(
                get_interval(1, '2017-09-01'),
                (date(year=2017, month=9, day=1), date(year=2017, month=9, day=30))
            )
