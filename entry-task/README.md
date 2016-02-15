# Entry task for Python Master - currency converter

Currency converter script implemented in Python 2.7. Returns JSON result.

## Usage
Run `currency_converter.py` with following parameters:
* --amount \<float\> ... amount of money to convert (required)
* --input_currency \<currency code\> ... from currency (required)
* --output_currency \<currency code\> ... to currency (if missing, convert to all currencies)

### Example
`python currency_converter.py --amount 10 --input_currency EUR --output_currency CZK`

`{"input": {"currency": "EUR", "amount": 10.0}, "output": {"CZK": 270.22}}`

## Functionality
### How conversion works
The script uses [Open Exchange Rates](https://openexchangerates.org) API (free version) to get current exchange rates with base in USD.
API key is saved in `/config.txt` file which is not present in this repository.
#### Amount calculation
1. Convert input amount to correct (base) amount in USD (rounded to 6 decimal places).
2. Convert base amount to amount in output currency (rounded to 2 decimal places).

The script checks if the entered currency codes exist and if the input amount is a number.

### Exchange rates
Because the "Forever Free" API plan has a limit of 1000 requests per month, the script was developed by parsing downloaded JSON input from API.
To make the script more useful/interesting, there are two basic ways, how the script gets the rates to work with.
The behaviour is determined in the `currency_converter.py` while creating the main object:
`converter = CurrencyConverter(app_id, <rates_read_mode>, <rates_filepath>)`

#### Rates read modes
1. "api" ... Just a HTTP GET call to API.
2. "file" ... JSON file saved on server (`/rates_files/latest.json`), which is automatically updated when it's older than 1 hour.
3. "file_no_update" ... JSON file, but with no update (useful for tests).

The constructor checks validity of the entered read modes and if rates file exists (if it's entered).

## Tests
Tests can be performed by running `cc_test.py`.

A test class (`TestCurrencyConverter`) tests class `src.CurrencyConverter` - its constructor and `convert` method.
File `/rates_files/test_rates.json` is used for exchange rates.



