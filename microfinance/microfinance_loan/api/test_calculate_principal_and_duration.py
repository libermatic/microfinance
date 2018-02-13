# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and Contributors
# See license.txt

from __future__ import unicode_literals
import unittest
import frappe

from microfinance.microfinance_loan.api.calculate_principal_and_duration \
    import execute as calculate_principal_and_duration

test_dependencies = ['Loan Plan']

class TestCalculatePrincipalAndDuration(unittest.TestCase):

    def test_calculate_principal_and_duration(self):
        '''Test calculate_principal_and_duration default case'''
        actual = calculate_principal_and_duration(
                20000.0,
                '_Test Loan Plan 1',
                '2030-08-19',
                '2017-12-12',
            )
        expected = {
                'principal': 480000.0,
                'expected_eta': '2023-01-04',
                'duration': 60,
                'recovery_amount': 8000.0,
                'initial_interest': 24000.0,
            }
        self.assertEqual(actual, expected)

    def test_calculate_principal_and_duration_end_date_before_loan_plan_max_duration(self):
        '''
            Test calculate_principal_and_duration when the end_date is before
            Loan Plan.max duration.
        '''
        actual = calculate_principal_and_duration(
                20000.0,
                '_Test Loan Plan 1',
                '2020-08-19',
                '2017-12-12',
            )
        expected = {
                'principal': 248000.0,
                'expected_eta': '2020-08-04',
                'duration': 31,
                'recovery_amount': 8000.0,
                'initial_interest': 12500.0,
            }
        self.assertEqual(actual, expected)

    def test_calculate_principal_force_duration(self):
        '''
            Test calculate_principal_and_duration when the end_date is ignored
            in Loan Plan.
        '''
        actual = calculate_principal_and_duration(
                20000.0,
                '_Test Loan Plan 3',
                '2020-08-19',
                '2017-12-12',
            )
        expected = {
                'principal': 480000.0,
                'expected_eta': '2023-01-04',
                'duration': 60,
                'recovery_amount': 8000.0,
                'initial_interest': 24000.0,
            }
        self.assertEqual(actual, expected)

    def test_calculate_principal_and_duration_raises_error(self):
        '''
            Test whether Loan Plan fields are missing
        '''
        params = (20000.0, '_Test Loan Plan 2', '2020-08-19')
        with self.assertRaises(ValueError):
            calculate_principal_and_duration(*params)

    def test_calculate_principal_and_duration_when_plan_is_dict(self):
        '''Test when loan_plan param is a dict'''
        actual = calculate_principal_and_duration(
                20000.0,
                {
                    'income_multiple': 24,
                    'max_duration': 60,
                    'billing_day': 5,
                    'rate_of_interest': 5.0,
                },
                '2020-08-19',
                '2017-12-12',
            )
        expected = {
                'principal': 248000.0,
                'expected_eta': '2020-08-04',
                'duration': 31,
                'recovery_amount': 8000.0,
                'initial_interest': 12400.0,
            }
        self.assertEqual(actual, expected)

    def test_calculate_principal_and_duration_raises_when_invalid_plan(self):
        '''
            Test for invalid Loan Plan dict
        '''
        params = (20000.0, 104, '2020-08-19')
        with self.assertRaises(ValueError):
            calculate_principal_and_duration(*params)
