import json
import urllib2


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
        if source == 'file':
            with open(self.rates_filepath) as rates_file:
                return json.load(rates_file)
        elif source == 'api':
            rates_json = urllib2.urlopen(self.rates_url).read()
            return json.loads(rates_json)
        else:
            raise ValueError("Unsupported way of getting rates.")
