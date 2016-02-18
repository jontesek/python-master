# Entry task for Python Master - currency converter

Currency converter script implemented in Python 2.7. No external modules used.

## Usage
Run `/currency_converter.py` with following parameters:
* `--amount <float>` ... Amount of money to convert (required).
* `--input_currency <3 letter currency code or currency symbol>` ... From currency (required).
* `--output_currency <3 letter currency code or currency symbol>` ... To currency (if missing, convert to all currencies).
* `--help` ... show parameters information.

Note: The script was developed on Windows. To make it run on Linux directly (via `./currency_converter.py`), it must be set as executable and a command `dos2unix currency_converter.py` must be executed.

### Example
`python currency_converter.py --amount 10 --input_currency EUR --output_currency CZK`

`{"input": {"currency": "EUR", "amount": 10.0}, "output": {"CZK": 270.22}}`

## Functionality
### How conversion works
The script uses [Open Exchange Rates](https://openexchangerates.org) API (free version) to get current exchange rates with base in USD.
API key is saved in `/config.txt` file which is not present in this repository.

The script checks on input:
* If the input amount is >= 0 (number with minus sign might be an error).
* If the entered currency codes/symbols exist.

#### Amount calculation
1. Convert input amount to correct (base) amount in USD.
2. Convert base amount to amount in output currency.

_Example for 10 EUR -> CZK_:

1. How many dollars do I need to buy 10 euros? 10 / 0.9 = 11.1111111111 ... B (1 USD = 0.90 EUR)
2. How many CZK do I get for B dollars? B * 24.26 = 269.55 (1 USD = 24.26 CZK)

NOTE: Currencies on FOREX markets are traded in pairs, so the result might not be exactly the same as if the suitable base (other than USD) could be used.
Also there are slightly different rates for "buy" and "sell" options. Values used are probably the "central" rate.

### Curency symbols
The requirement was to allow entering also currency codes (such as $, € or ¥).
To make it possible, a database of symbols and corresponding codes had to be created.
Unlike for currency codes, there is no standard for symbols.

To create the database, [Currency symbol](https://en.wikipedia.org/wiki/Currency_symbol#List_of_presently-circulating_currency_symbols) Wiki page was parsed and all symbols of mentioned currencies were downloaded (see `/cur_symbols/parse_wiki.py`).
Later was discovered [another Wiki page](https://en.wikipedia.org/wiki/List_of_circulating_currencies) with a list of currencies for every country.
The list was merged and checked with the aforementioned symbols and the final TXT file was created (see `/cur_symbols/currency_symbols.txt`).

The file is read in constructor, where a dictionary (currency symbol -\> currency code) is created and made available for use in application.
But the problem is reading symbols from terminal, if the terminal does not use UTF-8 encoding (Windows). I tried to solve it, but it still does not work properly. On Linux (Ubuntu) the symbols are processed with no problems.

NOTE: Iranian rial (IRR) and Yemeni rial (YER) have unfortunately exactly the same symbol. So it was determined that in the final Python dictionary will only YER be present.
The same situation arose with Japanese yen (JPY) and Chinese yuan (CNY). To prefer a more democratic country, the JPY was chosen to be in the dictionary :).

### Exchange rates
Because the "[Forever Free](https://openexchangerates.org/signup)" API plan has a limit of 1000 requests per month, the script was developed by parsing downloaded JSON output from the API.
To make the script more useful/interesting, there are multiple ways, how the script gets the rates to work with.
The behaviour is determined in `/currency_converter.py` file while creating the main object:

`converter = CurrencyConverter(app_id, <rates_read_mode>, symbols_filepath, rates_filepath)`

#### Rates read modes
1. "api" ... Just a HTTP GET call to API.
2. "file" ... JSON file saved on server (`/rates_files/latest.json`), which is automatically updated when it's older than 1 hour.
3. "file_no_update" ... JSON file, but with no update (useful for tests).

The constructor checks validity of the entered read mode, if symbols file exists and if rates file exists (if it's entered).

This way the script can be used to serve far more than 1000 requests per month.
Of course, a better solution than a simple text file would be necessary in a real world scenario (i.e. Redis or other in-memory storage), but this is out of the scope of this assignment.

## Tests
Tests can be performed by running `/cc_tests.py`

A test class (`TestCurrencyConverter`) tests class `src.CurrencyConverter` - its constructor and `convert` method.
Both normal operation and exceptions are tested.
File `/rates_files/test_rates.json` is used for exchange rates.
