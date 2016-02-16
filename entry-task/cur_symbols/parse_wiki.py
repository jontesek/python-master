# -*- coding: UTF-8 -*-
import urllib2

from bs4 import BeautifulSoup

from TextWriter import TextWriter


# Get HTML page (https://en.wikipedia.org/wiki/Currency_symbol)
soup = BeautifulSoup(open('wiki_list.htm'), 'lxml')
# Find the table
table = soup.find('table', class_='wikitable sortable')
# Get rows
rows = table.find_all('tr')

# Save all links
links = {}

for row in rows[1:]:
    # Get symbol - link or no link?
    s_link = row.find_all('td')[0].find('a')
    if s_link:
        symbol = s_link.text.strip()
    else:
        symbol = row.find_all('td')[0].find(text=True, recursive=False).strip()
    # Get link
    url = row.find_all('td')[1].find('a').get('href')
    url = 'https://en.wikipedia.org'+url
    # Save symbol and link
    links[symbol] = url

# Visit all links and get currency code of the symbol
c_symbols = {}

#links = {'£': 'https://en.wikipedia.org/wiki/Pound_sterling'}

for symbol, url in links.items():
    print symbol, url
    #soup = BeautifulSoup(open('currency_page.htm'), 'lxml')
    # Get Wiki page
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page, 'lxml')
    # Find infobox
    table = soup.find('table', class_='infobox')
    # Check if the table was found - if not, it's a past currency.
    if not table:
        continue
    # Find ISO code
    iso_cell = table.find('a', title='ISO 4217')
    # Check if the code was found - if not, it's not a regular currency.
    if not iso_cell:
        continue
    cur_code = iso_cell.parent.parent.contents[3].text.strip()
    cur_name = soup.select('#firstHeading')[0].text.strip()
    # Save the code
    c_symbols[symbol] = [cur_code, cur_name]

# Create list from c_symbols
c_list = []
for symbol, (code, name) in c_symbols.items():
    c_list.append([code, symbol, name])

# Prepare header
header = ['currency code', 'currency symbol', 'currency name']
c_list.insert(0, header)

# Write list to file
tw = TextWriter()
tw.write_file(c_list, 'currency_symbols_raw', ';')
