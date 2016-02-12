#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

from src.CurrencyConverter import CurrencyConverter

# Get directory of the file.
current_dir = os.path.dirname(os.path.realpath(__file__))

# Get API key from config file.
with open(os.path.abspath(current_dir+'/config.txt')) as config_file:
    app_id = config_file.read().strip()

# Set rates filepath.
rates_filepath = os.path.abspath(current_dir+'/test_files/latest.json')

# Create the main object.
converter = CurrencyConverter(app_id, "file", rates_filepath)


# If the file was imported (as module).
def convert_money(amount, input_cur, output_cur=False):
    return converter.convert(amount, input_cur, output_cur)

# If the file was run directly (as script).
if __name__ == '__main__':
    # Module required command line parsing.
    import argparse

    # Parse the incoming arguments
    # example: ./currency_converter.py --amount 100.0 --input_currency EUR --output_currency CZK
    parser = argparse.ArgumentParser(description='Currency Converter in Python')
    parser.add_argument('--amount', action='store', help='amount of money to convert',
                        metavar='<float>', required=True)
    parser.add_argument('--input_currency', action='store', help='from currency',
                        metavar='<3 letter currency code>', required=True)
    parser.add_argument('--output_currency', action='store',
                        help='to currency | if missing, to all currencies', metavar='<3 letter currency code>')
    args = parser.parse_args()

    # Calculate the result.
    try:
        # Check if an output currency is set.
        if args.output_currency:
            result = converter.convert(float(args.amount), args.input_currency, args.output_currency)
        else:
            result = converter.convert(float(args.amount), args.input_currency)
    except Exception, e:
        raise SystemExit(e)

    # show result
    print(result)
