import os
from pprint import pprint

from src.CurrencyConverter import CurrencyConverter


app_id = 'f919f806b9674d3284f6afb19945e9fa'
rates_filepath = os.path.abspath('test_files/latest.json')

converter = CurrencyConverter(app_id, rates_filepath)

result = converter.convert(10, 'EUR', 'CZK')

pprint(result)

# command line stuff - get from KAS project
