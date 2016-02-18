# -*- coding: UTF-8 -*-
import json
import urllib2
import time
import os.path

# Workaround for Windows terminal encoding
import codecs
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)


class CurrencyConverter(object):
    """
    Main class for currency conversion (via convert() method).
    Supports reading rates from API or file and working with symbols.
    """

    def __init__(self, app_id, rates_read_mode, symbols_filepath, rates_filepath=False):
        """
        Args:
            app_id (string): API key for openexchangerates.org.
            rates_read_mode (string): "api", "file", "file_no_update".
            symbols_filepath (string): Absolute path to the Currency symbols file.
            rates_filepath (string): Absolute path to the Rates file.

        Raises:
            ValueError: Invalid rates_read_mode value.
            IOError: Rates file does not exist. | Currency symbols file does not exist.
            IndexError: Currency symbols file could not be properly parsed.
        """
        # Set the correct API URL
        self.rates_url = 'https://Xopenexchangerates.org/api/latest.json?app_id='+app_id

        # PARAMETERS CHECK
        # Check rates_read_mode validity.
        if rates_read_mode not in ['file', 'file_no_update', 'api']:
            msg = 'Rates_read_mode has invalid value: ' + rates_read_mode + \
                  '. It must be "api", "file" or "file_no_update".'
            raise ValueError(msg, 4)
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
        # Get currency symbols.
        try:
            self.currency_symbols = self._read_currency_symbols(symbols_filepath)
        except IndexError:
            msg = 'Currency symbols file has an invalid format. ' \
                  'It should be: header \\n <cur code>\\t<cur symbol> \\n...'
            raise IndexError(msg)

    def convert(self, in_amount, input_cur, output_cur=None, terminal_encoding=None):
        """
        Convert given amount of money in input currency to actual amount of money in output currency.
        If output currency parameter is missing, convert the amount to all known currencies.

        Args:
            in_amount (float | int): Amount of money to convert.
            input_cur (string): From currency (3 letter currency code or currency symbol).
            output_cur (string | None): To currency (3 letter currency code or currency symbol).
            terminal_encoding (string | None): Encoding of the input_cur and output_cur parameters (default is utf-8).

        Returns:
            JSON string in the following format (example for EUR -> CZK conversion):
            {
                "input": {
                    "amount": 100.0,
                    "currency": "EUR"
                },
                "output": {
                    "CZK": 2707.36
                }
            }

        Raises:
            ValueError: Unknown currency code or symbol. | Input is not a number. | Invalid JSON response or file.
            urllib2.HTTPError: Could not download data from the API.
            urllib2.URLError: No internet connection / invalid domain name in API URL.
            IOError: Could not read Rates file.
        """
        # Get current exchange rates
        try:
            rates_data = self._get_rates(self.rates_read_mode)
        except urllib2.HTTPError, e:
            msg = "There was an error while getting data from the API.\n" + e.msg
            raise urllib2.HTTPError(e.url, e.code, msg, e.hdrs, e.fp)
        except urllib2.URLError, e:
            msg = "There is no internet connection or domain name in API URL is invalid.\n" + str(e)
            raise urllib2.URLError(msg)
        except IOError, e:
            msg = "Could not read Rates file.\n" + e.message
            raise IOError(msg)

        # Select exchange rates
        rates = rates_data['rates']

        # Remove surrounding whitespace characters from inputs.
        input_cur = input_cur.strip()
        output_cur = output_cur.strip()

        # If run from terminal, decode input values. Necessary only for reading symbols from Windows terminal.
        if terminal_encoding:
            input_cur = unicode(input_cur, terminal_encoding).encode('utf-8')
            if output_cur:
                output_cur = unicode(output_cur, terminal_encoding).encode('utf-8')

        # Check if input currency is valid.
        if input_cur not in rates and input_cur not in self.currency_symbols:
            raise ValueError("Unknown input currency code/symbol entered: " + input_cur, 5)
        # Check if output currency is valid.
        if output_cur and (output_cur not in rates and output_cur not in self.currency_symbols):
            raise ValueError("Unknown output currency code/symbol entered: " + output_cur, 5)
        # Check if the input amount is a number.
        if not isinstance(in_amount, (int, long, float)):
            raise ValueError("Input amount is not a number: " + in_amount, 6)

        # If currency symbol is entered, find the coresponding code.
        if input_cur not in rates:
            input_cur = self.currency_symbols[input_cur]
        if output_cur and output_cur not in rates:
            output_cur = self.currency_symbols[output_cur]

        # AMOUNT CALCULATION
        # Example for 10 EUR -> CZK:
        #   1. How many dollars do I need to buy 10 euros? 10 / 0.9 = 11.1111111111 ... B (1 USD = 0.90 EUR)
        #   2. How many CZK do I get for B dollars? B * 24.26 = 269.55 (1 USD = 24.26 CZK)

        # Calculate amount in the base currency.
        base_amount = float(in_amount) / rates[input_cur]

        # Calculate amount in the output currency/all currencies (based on the amount in the base currency).
        out_amounts = {}
        if output_cur:
            out_amounts[output_cur] = round(base_amount * rates[output_cur], 2)
        else:
            for cur_code, exchange_rate in rates.items():
                out_amounts[cur_code] = round(base_amount * exchange_rate, 2)

        # Create the final return object.
        result_dict = {
            'input': {
                'amount': in_amount,
                'currency': input_cur,
            },
            'output': out_amounts,
        }
        # Convert dict to JSON string.
        return json.dumps(result_dict)

    def _get_rates(self, source):
        """
        Get actual exchange rates for all known currencies.

        Args:
            source (string): "api", "file", "file_no_update"

        Returns:
            Dictionary containing base currency, rates (code and value pairs) and UNIX timestamp (time of the rates).
            Example:
            {
                "timestamp": 1455274808,
                "base": "USD",
                "rates": {
                    "AED": 3.673075,
                    "AFN": 68.879999,
                    <... 171 currencies in total>
                }
            }

        Raises:
            ValueError: No JSON object could be decoded -> invalid JSON response or file. | Invalid source parameter
            urllib2.HTTPError: Could not download data from API.
            IOError: Rates file could not be read/written.
        """
        # Get data from API.
        if source == 'api':
            rates_json = urllib2.urlopen(self.rates_url).read()
            return self._convert_rates_json_to_dict(rates_json)

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
                    # If it is, get new rates from API, update the file and return rates.
                    return self._get_api_rates_and_save_to_file()
                else:
                    # If not, just return the present rates.
                    return rf_dict
        # Invalid source parameter.
        else:
            raise ValueError("Unsupported way of getting rates: " + source)

    def _get_api_rates_and_save_to_file(self):
        """
        Get rates from API, save them to file and return the rates dictionary.

        Returns:
            Dictionary with keys "timestamp", "base" and "rates".
        """
        try:
            rates_json = urllib2.urlopen(self.rates_url).read()
            rates_dict = self._convert_rates_json_to_dict(rates_json)
            final_json = json.dumps(rates_dict)
            with open(self.rates_filepath, 'w') as rates_file:
                rates_file.write(final_json)
            return rates_dict
        # If there is no answer or file write is impossible, at least return last known rates.
        except (urllib2.HTTPError, IOError):
            with open(self.rates_filepath) as rates_file:
                return json.load(rates_file)

    @staticmethod
    def _convert_rates_json_to_dict(rates_json):
        """
        Convert rates from API (JSON string) to Python dictionary.
        Preserve only necessary items.
        Make sure all values are in a suitable format (i.e. timestamp must be UNIX timestamp).

        Args:
            rates_json (string): JSON result from API.

        Returns:
            Dictionary with fields: "base", "timestamp", "rates" - see self._get_rates() docstring for details.
        """
        # Convert JSON to dictionary.
        r_dict = json.loads(rates_json)
        # Remove unnecessary items.
        r_dict.pop("disclaimer")
        r_dict.pop("license")
        # Result
        return r_dict

    @staticmethod
    def _read_currency_symbols(symbols_filepath):
        """
        Read currency symbols from a file and return them as dictionary.

        Args:
            symbols_filepath (string): Absolute filepath to the currency symbols file.

        Returns:
            Dictionary with currency symbol as key and currency code as value. Example:
            {
                '€': 'EUR',
                '¥': 'JPY',
            }
            Note: There might be multiple symbols (keys) for one currency code (value).
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
