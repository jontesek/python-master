# -*- coding: UTF-8 -*-
import os

from src.CurrencyConverter import CurrencyConverter

#import currency_converter
#print(currency_converter.convert_money(10,'EUR'))

# Get API key from config file
with open('config.txt') as config_file:
    app_id = config_file.read().strip()

# Filepaths
current_dir = os.path.dirname(os.path.realpath(__file__))
rates_filepath = os.path.abspath(current_dir+'/rates_files/latest.json')
symbols_filepath = os.path.abspath(current_dir+'/cur_symbols/currency_symbols.txt')

# The main object
converter = CurrencyConverter(app_id, 'file_no_update', symbols_filepath, rates_filepath)

# Codes test
#result = converter.convert(10, 'EUR', 'CZK')
#result = converter.convert(10, 'EUR', 'EFKA')
#result = converter.convert(10, 'EUR')
#result = converter.convert(100, 'CZK', 'USD')

# Symbols test
result = converter.convert(10, '€', 'CZK')
result = converter.convert(111, 'CZK', '€')
result = converter.convert(111, 'Kč', '€')
result = converter.convert(500.5, '¥', '$')
result = converter.convert(1000, '₸', 'zł')

# JSON
print(result)
