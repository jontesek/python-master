from src.CurrencyConverter import CurrencyConverter


api_credentials = {

}

converter = CurrencyConverter(api_credentials)

converter.convert(10, 'USD', 'CZK')


# command line stuff - get from KAS project
