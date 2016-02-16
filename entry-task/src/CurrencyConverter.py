# -*- coding: UTF-8 -*-
import json
import urllib2
import time
import os.path

# workaround for microsoft encoding
import codecs
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)


class CurrencyConverter(object):

    def __init__(self, app_id, rates_read_mode, symbols_filepath, rates_filepath=False):
        """
        Args:
            app_id (string): API key for openexchangerates.org.
            rates_read_mode (string): "api", "file", "file_no_update".
            rates_filepath (string): Absolute path to the rates file.

        Raises:
            ValueError: Invalid rates_read_mode value.
            IOError: Rates file does not exist.
        """
        # Set the correct API URL
        self.rates_url = 'https://openexchangerates.org/api/latest.json?app_id='+app_id
        ## PARAMETERS CHECK
        # Check rates_read_move validity.
        if rates_read_mode not in ['file', 'file_no_update', 'api']:
            raise ValueError("Rates_read_move invalid value.")
        # Check if symbols file exists.
        if not os.path.isfile(symbols_filepath):
            raise IOError('Wrong path to the Currency symbols file: ' + symbols_filepath, 3)
        # Check if rates file is set, it exists.
        if rates_filepath and not os.path.isfile(rates_filepath):
            raise IOError('Wrong path to the Rates file: ' + rates_filepath, 1)
        # If rates file is missing, rates_read_mode must be set to "api".
        if not rates_filepath and rates_read_mode != 'api':
            raise ValueError("If rates file is missing, rates_read_mode must be set to 'api'.", 2)

        # Set variables.
        self.rates_filepath = rates_filepath
        self.rates_read_mode = rates_read_mode
        self.currency_symbols = self._read_currency_symbols(symbols_filepath)

    def convert(self, in_amount, input_cur, output_cur=False, terminal_encoding=False):
        """
        Convert given amount of money in input currency to actual amount of money in output currency.
        If output currency parameter is missing, convert to all known currencies.

        Args:
            in_amount (float | int): Amount of money to convert.
            input_cur (string): From currency (3 letter code or currency symbol).
            output_cur (string | False): To currency (3 letter code or currency symbol).
            terminal_encoding (string | False): Encoding of the input_cur and output_cur parameters (default is utf-8).

        Returns:
            JSON string in the following format:
            {
                "input": {
                    "amount": 100.0,
                    "currency": "EUR"
                },
                "output": {
                    "CZK": 2707.36,
                }
            }

        Raises:
            ValueError: Unknown currency code or symbol. | Input is not a number. | Invalid JSON response or file.
            urllib2.HTTPError: Could not download data from the API.
            IOError: Could not read Rates file.
        """
        # Get current rates
        try:
            rates_data = self._get_rates(self.rates_read_mode)
        except urllib2.HTTPError, e:
            msg = "There was an error while downloading data from the API.\n" + e.message
            raise urllib2.HTTPError(msg)
        except IOError, e:
            msg = "Could not read Rates file.\n" + e.message
            raise IOError(msg)

        # Get main values
        rates = rates_data['rates']

        # If needed, decode input values.
        if terminal_encoding:
            input_cur = unicode(input_cur, terminal_encoding).encode('utf-8')
            output_cur = unicode(output_cur, terminal_encoding).encode('utf-8')

        # Check if input currency is valid.
        if input_cur not in rates and input_cur not in self.currency_symbols:
            raise ValueError("Unknown input currency code/symbol entered: " + input_cur, 5)
        # Check if output currency is valid.
        if output_cur is not False and (output_cur not in rates and output_cur not in self.currency_symbols):
            raise ValueError("Unknown output currency code/symbol entered: " + output_cur, 5)
        # Check if the input amount is a number.
        if not isinstance(in_amount, (int, long, float)):
            raise ValueError("Input amount is not a number.", 6)

        # If currency symbol is entered, find the coresponding code.
        if input_cur not in rates:
            input_cur = self.currency_symbols[input_cur]
        if output_cur is not False and output_cur not in rates:
            output_cur = self.currency_symbols[output_cur]

        # Calc amount in the base currency.
        base_amount = float(in_amount) / rates[input_cur]

        # Calculate amount in the output currency/all currencies (based on amount in base currency).
        out_amounts = {}
        if output_cur:
            out_amounts[output_cur] = round(base_amount * rates[output_cur], 2)
        else:
            for ccode, exchange_rate in rates.items():
                out_amounts[ccode] = round(base_amount * exchange_rate, 2)

        # Create the final return object
        result_dict = {
            'input': {
                'amount': in_amount,
                'currency': input_cur,
            },
            'output': out_amounts,
        }
        return json.dumps(result_dict)

    def _get_rates(self, source):
        """
        Get actual exchange rates for all known currencies.

        Args:
            source (string): "api", "file", "file_no_update"

        Returns:
            Dictionary containing base currency, rates (code and value pairs ) and UNIX timestamp (time of the rates).
            For example:
            {
                "timestamp": 1455274808,
                "base": "USD",
                "rates": {
                    "AED": 3.673075,
                    "AFN": 68.879999,
                    ...
                }
            }

        Raises:
            ValueError: No JSON object could be decoded -> invalid JSON response or file.
            urllib2.HTTPError: Could not download data from API.
            IOError: Rates file could not be read/written.
        """
        # Get data from API.
        if source == 'api':
            rates_json = urllib2.urlopen(self.rates_url).read()
            return self._edit_rates_dict(json.loads(rates_json))

        # Get data from rates file.
        if source == 'file' or source == 'file_no_update':
            with open(self.rates_filepath) as rates_file:
                # Get data from the file.
                rf_dict = json.load(rates_file)
                # If set, just return the file (no update).
                if source == 'file_no_update':
                    return rf_dict
                # Check if the file is older than 1 hour.
                if rf_dict['timestamp'] < (int(time.time()) - 3600):
                    source = 'api_save'     # continue with the code below
                else:
                    return rf_dict

        # Get data from API and save result to rates file.
        if source == 'api_save':
            try:
                rates_json = urllib2.urlopen(self.rates_url).read()
                rates_dict = self._edit_rates_dict(json.loads(rates_json))
                final_json = json.dumps(rates_dict)
                with open(self.rates_filepath, 'w') as rates_file:
                    rates_file.write(final_json)
                return rates_dict
            # If there is no answer or file write is impossible, at least return last known rates.
            except (urllib2.HTTPError, IOError):
                with open(self.rates_filepath) as rates_file:
                    return json.load(rates_file)

        else:
            raise ValueError("Unsupported way of getting rates.")

    @staticmethod
    def _edit_rates_dict(r_dict):
        """
        Edit rates dictionary so it contains only necessary items in a suitable format.

        Args:
            r_dict (dict): Result from API.

        Returns:
            Normalized dict with fields: "base", "timestamp", "rates"
        """
        # Remove unnecessary items
        r_dict.pop("disclaimer")
        r_dict.pop("license")
        # result
        return r_dict

    @staticmethod
    def _read_currency_symbols(symbols_filepath):
        """
        Read currency symbols from a file and returns them as dictionary.

        Args:
            symbols_filepath (string): Absolute filepath to the currency symbols file.

        Returns:
            Dictionary with symbol as key and currency code as value. Example:
            {
                '€': 'EUR',
                '¥': 'JPY',
            }
        """
        # Open file
        c_file = open(symbols_filepath)
        c_file.readline()  # skip header line
        # Read symbols into dict
        symbols = {}
        for line in c_file:
            l_items = line.split('\t')
            c_code = l_items[0].strip()
            c_symbol = l_items[1].strip()
            symbols[c_symbol] = c_code
        c_file.close()
        # Result
        return symbols
