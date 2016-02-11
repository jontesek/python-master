import json
import urllib2

from pprint import pprint


class CurrencyConverter(object):

    def __init__(self, app_id, rates_filepath):
        # set the correct API URL
        self.rates_url = 'https://openexchangerates.org/api/latest.json?app_id='+app_id
        self.rates_filepath = rates_filepath

    def convert(self, in_amount, input_cur, output_cur=False):
        """
        Convert given amount of money in input currency to actual amount of money in output currency.
        :param in_amount: float
        :param input_cur: string
        :param output_cur: string or False
        :return: JSON
        """
        # Get current rates
        try:
            rates_data = self._get_rates('file')
            base = rates_data['base']
            rates = rates_data['rates']
            # Calc amount in the base currency.
            base_amount = in_amount / float(rates[input_cur])
            # Calc amount in the output currency (based on amount in base currency).
            out_amount = base_amount * rates[output_cur]
            # Create a final return object
            return out_amount

        except IOError, e:
            print("Could not read Rates file.")
            print(e)
        except urllib2.HTTPError, e:
            print("There was an error while downloading data from the API.")
            print(e)


    def _get_rates(self, source):
        """
        Returns dictionary with "base" (base currency), "rates", "date" fields.
        :param source: file or api
        :return: dictionary
        """
        if source == 'file':
            with open(self.rates_filepath) as rates_file:
                return json.load(rates_file)
        elif source == 'api':
            rates_json = urllib2.urlopen(self.rates_url).read()
            return json.loads(rates_json)
        else:
            raise ValueError("Unsupported way of getting rates.")
