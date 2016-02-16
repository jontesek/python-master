#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import os.path
import json

from src.CurrencyConverter import CurrencyConverter

# Filepaths
current_dir = os.path.dirname(os.path.realpath(__file__))
rates_filepath = os.path.abspath(current_dir+'/rates_files/test_rates.json')

# Get API key from config file
with open(os.path.abspath(current_dir+'/config.txt')) as config_file:
    app_id = config_file.read().strip()


# Test class
class TestCurrencyConverter(unittest.TestCase):

    def setUp(self):
        self.c_converter = CurrencyConverter(app_id, 'file_no_update', rates_filepath)

    # Test constructor

    def test_construct_1(self):
        """When rates file is set, but does not exists, raise an exception."""
        with self.assertRaises(IOError) as context:
            CurrencyConverter(app_id, 'file', 'XYZ.XXX')
        self.assertTrue(1 in context.exception)

    def test_construct_2(self):
        """When rates file is missing, but rates_read_mode is not set to 'api', raise an exception."""
        with self.assertRaises(ValueError) as context:
            CurrencyConverter(app_id, 'file')
        self.assertTrue(2 in context.exception)

    def test_construct_3(self):
        """Rates file is set and exists."""
        try:
            CurrencyConverter(app_id, 'file', rates_filepath)
        except Exception, e:
            self.fail(e)

    def test_construct_4(self):
        """Rates file is missing and rates_rad_mode is set to 'api'."""
        try:
            CurrencyConverter(app_id, 'api')
        except Exception, e:
            self.fail(e)

    # Test convert method - exceptions

    def test_convert_1(self):
        """When input amount is not a number, raise an exception."""
        with self.assertRaises(ValueError) as context:
            self.c_converter.convert('wro145ng', 'EUR', 'CZK')
        self.assertTrue(6 in context.exception)

    def test_convert_2(self):
        """When an unknown input currency code is entered, raise an exception."""
        with self.assertRaises(ValueError) as context:
            self.c_converter.convert(10, 'XEUR', 'CZK')
        self.assertTrue(5 in context.exception)

    def test_convert_3(self):
        """When an unknown output currency code is entered, raise an exception."""
        with self.assertRaises(ValueError) as context:
            self.c_converter.convert(10, 'EUR', 'XCZK')
        self.assertTrue(5 in context.exception)

    # Test convert method - returned JSON

    def test_convert_json(self):
        """Check if the returned string is valid JSON with given structure and correct content."""
        result_str = self.c_converter.convert(10, 'EUR', 'CZK')
        try:
            # Read JSON string to Python dictionary
            r_dict = json.loads(result_str)
            # Check input fields
            j_input = r_dict['input']
            if j_input['amount'] != 10 or j_input['currency'] != 'EUR':
                raise ValueError("Incorrect input fields.")
            # Check output fields
            if r_dict['output']['CZK'] != 270.26:
                raise ValueError("Incorrect output value.")
        except ValueError, e:
            msg = 'Convert() method does not return a valid JSON string with correct content.\n' + str(e)
            self.fail(msg)
        except KeyError, e:
            msg = 'Convert() method does not return JSON string with necessary fields.\n' + str(e)
            self.fail(msg)

    # Test convert method - output values

    def test_convert_4(self):
        """Convert EUR to all currencies."""
        dict_data = json.loads(self.c_converter.convert(10, 'EUR'))
        out_amounts = dict_data['output']
        self.assertGreater(len(out_amounts), 100)

    def test_convert_5(self):
        """Convert EUR to CZK."""
        dict_data = json.loads(self.c_converter.convert(10, 'EUR', 'CZK'))
        out_amount = dict_data['output']['CZK']
        self.assertEqual(out_amount, 270.26)

    def test_convert_6(self):
        """Convert USD to CZK."""
        dict_data = json.loads(self.c_converter.convert(10, 'USD', 'CZK'))
        out_amount = dict_data['output']['CZK']
        self.assertEqual(out_amount, 239.45)

    def test_convert_7(self):
        """Convert CZK to USD."""
        dict_data = json.loads(self.c_converter.convert(239.4491, 'CZK', 'USD'))
        out_amount = dict_data['output']['USD']
        self.assertEqual(out_amount, 10)


# Run all tests when the file is run from terminal.
if __name__ == '__main__':
    unittest.main()
