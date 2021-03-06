#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys

from src.CurrencyConverter import CurrencyConverter

# Get directory of the file.
current_dir = os.path.dirname(os.path.realpath(__file__))

# Get API key from config file.
with open(os.path.abspath(current_dir+'/config.txt')) as config_file:
    app_id = config_file.read().strip()

# Set filepaths
rates_filepath = os.path.abspath(current_dir+'/rates_files/latest.json')
symbols_filepath = os.path.abspath(current_dir+'/cur_symbols/currency_symbols.txt')

# Create the main object.
converter = CurrencyConverter(app_id, 'api', symbols_filepath, rates_filepath)


# If the file was imported (as module).
def convert_money(amount, input_cur, output_cur=None):
    return converter.convert(amount, input_cur, output_cur)

# If the file was run directly (as script).
if __name__ == '__main__':
    # Module required for command line parsing.
    import argparse

    # Save terminal encoding
    terminal_encoding = sys.stdin.encoding

    # Parse the incoming arguments
    # example 1: ./currency_converter.py --amount 100.0 --input_currency EUR --output_currency CZK
    # example 2: ./currency_converter.py --amount 0.9 --input_currency ¥ --output_currency AUD
    parser = argparse.ArgumentParser(description='Currency Converter in Python')
    parser.add_argument('--amount', action='store', help='Amount of money to convert',
                        metavar='<float>', required=True)
    parser.add_argument('--input_currency', action='store', help='From currency',
                        metavar='<3 letter currency code or currency symbol>', required=True)
    parser.add_argument('--output_currency', action='store',
                        help='To currency | If missing, to all currencies.',
                        metavar='<3 letter currency code or currency symbol>')
    args = parser.parse_args()

    # Calculate the result.
    try:
        result = converter.convert(args.amount, args.input_currency, args.output_currency, terminal_encoding)
    except Exception, e:
        raise SystemExit(e)

    # Show JSON string
    print(result)
