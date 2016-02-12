import json
import urllib2
import time
import os.path


class CurrencyConverter(object):

    def __init__(self, app_id, rates_read_mode, rates_filepath=False):
        """
        Constructor
        :param app_id: API key for openexchangerates.org API.
        :param rates_read_mode: file | api
        :param rates_filepath: Absolute path to the rates file.
        :return:
        """
        # Set the correct API URL
        self.rates_url = 'https://openexchangerates.org/api/latest.json?app_id='+app_id
        # Check if rates file is set and exists.
        if rates_filepath and not os.path.isfile(rates_filepath):
            raise ValueError('Wrong path to the Rates file: ' + rates_filepath)
        # If rates file is missing, rates_read_mode must be set to "api".
        if not rates_filepath and rates_read_mode != 'api':
            raise ValueError("If rates file is missing, rates_read_mode must be set to 'api'.")
        # Set it and rates read mode.
        self.rates_filepath = rates_filepath
        self.rates_read_mode = rates_read_mode

    def convert(self, in_amount, input_cur, output_cur=False):
        """
        Convert given amount of money in input currency to actual amount of money in output currency.
        :param in_amount: float
        :param input_cur: string
        :param output_cur: string or False
        :return: JSON result
        """
        # Get current rates
        try:
            rates_data = self._get_rates(self.rates_read_mode)
        except urllib2.HTTPError, e:
            print("There was an error while downloading data from the API.")
            print(e)
            return False
        except IOError, e:
            print("Could not read Rates file.")
            print(e)
            return False

        # Get main values
        rates = rates_data['rates']

        # Check if currency codes are valid.
        if input_cur not in rates or (output_cur is not False and output_cur not in rates):
            raise ValueError("Unknow currency code entered.")

        # Calc amount in the base currency.
        base_amount = in_amount / rates[input_cur]

        # Calculate amount in the output currency/all currencies (based on amount in base currency).
        out_amounts = {}
        if output_cur:
            out_amounts[input_cur] = base_amount * rates[output_cur]
        else:
            for ccode, exchange_rate in rates.items():
                out_amounts[ccode] = base_amount * exchange_rate

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
        Returns dictionary with "base" (base currency), "rates", "timestamp" fields.
        :param source: file or api
        :return: dictionary
        """
        # Get data from API.
        if source == 'api':
            rates_json = urllib2.urlopen(self.rates_url).read()
            return json.loads(rates_json)

        # Get data from rates file.
        if source == 'file':
            with open(self.rates_filepath) as rates_file:
                # Get data from the file.
                rf_dict = json.load(rates_file)
                # Check if the file is older than 1 hour.
                if rf_dict['timestamp'] < (int(time.time()) - 3600):
                    source = 'api_save'     # continue with the code below
                else:
                    return rf_dict

        # Get data from API and save result to rates file.
        if source == 'api_save':
            try:
                rates_json = urllib2.urlopen(self.rates_url).read()
                with open(self.rates_filepath, 'w') as rates_file:
                    rates_file.write(rates_json)
                return json.loads(rates_json)
            # If there is no connection, at least return last known rates.
            except Exception:
                with open(self.rates_filepath) as rates_file:
                    return json.load(rates_file)

        else:
            raise ValueError("Unsupported way of getting rates.")
