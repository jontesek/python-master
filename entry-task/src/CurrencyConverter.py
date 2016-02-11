
class CurrencyConverter(object):

    def __init__(self, api_credentials):
        # set api credentials
        self.api_cred = api_credentials

    def convert(self, amount, input_cur, output_cur=False):
        """
        Convert given amount of money in input currency to actual amount of money in output currency.
        :param amount: float
        :param input_cur: string
        :param output_cur: string or False
        :return: JSON
        """

