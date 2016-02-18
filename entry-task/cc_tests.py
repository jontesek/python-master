#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os.path
import json

from src.CurrencyConverter import CurrencyConverter

# Filepaths
current_dir = os.path.dirname(os.path.realpath(__file__))
rates_filepath = os.path.abspath(current_dir+'/rates_files/test_rates.json')
symbols_filepath = os.path.abspath(current_dir+'/cur_symbols/currency_symbols.txt')

# Get API key from config file
with open(os.path.abspath(current_dir+'/config.txt')) as config_file:
    app_id = config_file.read().strip()


# Test class
class TestCurrencyConverter(unittest.TestCase):
    """
    Performs tests for public methods of CurrencyConverter class - constructor and convert method.
    Uses pre-defined rates file so the exchange rates do not change and therefore results can be checked.
    """

    def setUp(self):
        """Create an object which will be used for testing convert() method."""
        self.c_converter = CurrencyConverter(app_id, 'file_no_update', symbols_filepath, rates_filepath)

    # Test constructor - exceptions

    def test_construct_1(self):
        """If rates file is set, but does not exist, raise an exception."""
        with self.assertRaises(IOError) as context:
            CurrencyConverter(app_id, 'file', symbols_filepath, 'XYZ.XXX')
        self.assertTrue(1 in context.exception)

    def test_construct_2(self):
        """If rates file is missing, but rates_read_mode is not set to 'api', raise an exception."""
        with self.assertRaises(ValueError) as context:
            CurrencyConverter(app_id, 'file', symbols_filepath)
        self.assertTrue(2 in context.exception)

    def test_construct_3(self):
        """If currency symbols file does not exist, raise an exception."""
        with self.assertRaises(IOError) as context:
            CurrencyConverter(app_id, 'file', 'XYZ.XXX', rates_filepath)
        self.assertTrue(3 in context.exception)

    def test_construct_4(self):
        """If invalid rates read mode is entered, raise an exception."""
        with self.assertRaises(ValueError) as context:
            CurrencyConverter(app_id, 'fXXXile', symbols_filepath, rates_filepath)
        self.assertTrue(4 in context.exception)

    # Test constructor - normal operation

    def test_construct_5(self):
        """Rates file is set and exists."""
        try:
            CurrencyConverter(app_id, 'file', symbols_filepath, rates_filepath)
        except Exception, e:
            self.fail(e)

    def test_construct_6(self):
        """Rates file is missing and rates_rad_mode is set to 'api'."""
        try:
            CurrencyConverter(app_id, 'api', symbols_filepath)
        except Exception, e:
            self.fail(e)

    # Test convert method - exceptions

    def test_convert_e1(self):
        """When input amount is not a number, raise an exception."""
        with self.assertRaises(ValueError) as context:
            self.c_converter.convert('wro145ng', 'EUR', 'CZK')
        self.assertTrue(6 in context.exception)

    def test_convert_e2(self):
        """When an unknown input currency code is entered, raise an exception."""
        with self.assertRaises(ValueError) as context:
            self.c_converter.convert(10, 'XEUR', 'CZK')
        self.assertTrue(5 in context.exception)

    def test_convert_e3(self):
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

    # Test convert method: If no output currency set, convert to all currencies.

    def test_convert_c1(self):
        """Convert EUR to all currencies."""
        dict_data = json.loads(self.c_converter.convert(10, 'EUR'))
        out_amounts = dict_data['output']
        self.assertGreater(len(out_amounts), 100)

    # Test convert method - currency codes

    def test_convert_c2(self):
        """Convert EUR to CZK."""
        dict_data = json.loads(self.c_converter.convert(10, 'EUR', 'CZK'))
        out_amount = dict_data['output']['CZK']
        self.assertEqual(out_amount, 270.26)

    def test_convert_c3(self):
        """Convert USD to CZK."""
        dict_data = json.loads(self.c_converter.convert(10, 'USD', 'CZK'))
        out_amount = dict_data['output']['CZK']
        self.assertEqual(out_amount, 239.45)

    def test_convert_c4(self):
        """Convert CZK to USD."""
        dict_data = json.loads(self.c_converter.convert(239.4491, 'CZK', 'USD'))
        out_amount = dict_data['output']['USD']
        self.assertEqual(out_amount, 10)

    # Test convert method - currency symbols

    def test_convert_s1(self):
        """€ (EUR) to CZK."""
        dict_data = json.loads(self.c_converter.convert(10, '€', 'CZK'))
        out_amount = dict_data['output']['CZK']
        self.assertEqual(out_amount, 270.26)

    def test_convert_s2(self):
        """CZK to € (EUR)."""
        dict_data = json.loads(self.c_converter.convert(111.88, 'CZK', '€'))
        out_amount = dict_data['output']['EUR']
        self.assertEqual(out_amount, 4.14)

    def test_convert_s3(self):
        """Kč (CZK) to € (EUR)."""
        dict_data = json.loads(self.c_converter.convert(111.88, 'Kč', '€'))
        out_amount = dict_data['output']['EUR']
        self.assertEqual(out_amount, 4.14)

    def test_convert_s4(self):
        """¥ (JPN) to $ (USD)."""
        dict_data = json.loads(self.c_converter.convert(500.5, '¥', '$'))
        out_amount = dict_data['output']['USD']
        self.assertEqual(out_amount, 4.45)

    def test_convert_s5(self):
        """৳ (BDT) to zł (PLN)."""
        dict_data = json.loads(self.c_converter.convert(1000, '৳', 'zł'))
        out_amount = dict_data['output']['PLN']
        self.assertEqual(out_amount, 49.65)

    def test_convert_s6(self):
        """£ (GBP) to all currencies."""
        dict_data = json.loads(self.c_converter.convert(11.11, '£', False))
        out_amounts = dict_data['output']
        self.assertGreater(len(out_amounts), 100)


# Run all tests when the file is run from terminal.
if __name__ == '__main__':
    unittest.main()
