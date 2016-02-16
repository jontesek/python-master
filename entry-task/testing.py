import os

from src.CurrencyConverter import CurrencyConverter
import currency_converter

# Get API key from config file
with open('config.txt') as config_file:
    app_id = config_file.read().strip()

# Filepaths
current_dir = os.path.dirname(os.path.realpath(__file__))
rates_filepath = os.path.abspath(current_dir+'/rates_files/latest.json')

# The main object
converter = CurrencyConverter(app_id, 'file', rates_filepath)

result = converter.convert(10, 'EUR', 'CZK')
#result = converter.convert(10, 'EUR', 'EFKA')
#result = converter.convert(10, 'EUR')
#result = converter.convert(100, 'CZK', 'USD')

#print(currency_converter.convert_money(10,'EUR'))

print(result)
