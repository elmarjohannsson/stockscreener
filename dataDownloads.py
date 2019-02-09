import bs4 as bs
import pickle
import os
import requests
import pandas as pd
import time
import sys
import shutil

import usedata
from settings import APIKEY

# The list of companies on Nasdaq Copenhagen. Should be updated once in a while to get changes.
def save_nasdaqcph_companies():
    # getting list of all the listed companies
    r = requests.get('http://www.nasdaqomxnordic.com/aktier/listed-companies/copenhagen', timeout=10)
    soup = bs.BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', {'id': 'listedCompanies'})
    companies = {}
    sectors = {}
    search = []
    for row in table.findAll('tr')[1:]:
        name = row.findAll('td')[0].text
        ticker = row.findAll('td')[1].text

        mapping_ticker = str.maketrans(' ', '-')   # changing the tickers to have same format.
        ticker = ticker.translate(mapping_ticker)
        ticker = ticker + '.CO'

        search.insert(0, [ticker, name])
        search.append([ticker, ticker])

        mapping_name = str.maketrans(r'\/:*?"><|óæøåü&ØÖÆÅÜ', '---------oeoau-OOEAU')  # name can't contain these chars.
        name = name.translate(mapping_name)

        currency = row.findAll('td')[2].text
        isin = row.findAll('td')[3].text
        sector = row.findAll('td')[4].text
        icb = row.findAll('td')[5].text
        omxc25 = False

        companies[ticker] = (isin, name, currency, sector, icb, omxc25)  # save it

        if sector not in sectors:  # add new sectors
            sectors[sector] = list()
    # print(search)

    with open('data/pickles/universe_companies.pickle', 'wb') as f:   # Dictionary with all companies. key:ticker values:isin, name, currency, sector, icb
        pickle.dump(companies, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('data/pickles/AllSectors.pickle', 'wb') as f:  # list of all the sectors on the market.
        pickle.dump(sectors, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('data/pickles/search.pickle', 'wb') as f:  # list with lists containing name and ticker.
        pickle.dump(search, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"finished getting the updated tickers on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

class CompanyFinancialData(object):
    def __init__(self, ticker, isin):
        self.ticker = ticker
        self.isin = isin

    def make_dir(self, update=False):
        if not os.path.isdir(f'data/CompanyData/{self.ticker}/'):
            os.makedirs(f'data/CompanyData/{self.ticker}/')
            self.download_all_financials()
        elif update:
            self.download_all_financials()

    def get_keyratios(self):
        url = (f'http://financials.morningstar.com/ajax/exportKR2CSV.html?t={self.isin}')
        r = requests.get(url)
        open(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', 'wb').write(r.content)
        # Try until it works.
        tries = 0
        while (os.stat(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs').st_size == 0 and tries < 5):
            try:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', 'wb').write(r.content)
                tries += 1
        print(f'Key Ratios for {self.ticker} finished')

    def get_income(self, period=12, number=3):
        url = (f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=is&period={period}&dataType=A&order=asc&columnYear=5&number={number}')
        r = requests.get(url)
        open(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', 'wb').write(r.content)
        # while error try until it works.
        tries = 0
        while (os.stat(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs').st_size == 0 and tries < 5):
            try:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', 'wb').write(r.content)
                tries += 1
        # print(f'Income Statement for {self.ticker} finished')

    def get_balancesheet(self, period=12, number=3):
        url = (f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=bs&period={period}&dataType=A&order=asc&columnYear=5&number={number}')
        r = requests.get(url)
        open(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', 'wb').write(r.content)
        # while error try until it works.
        tries = 0
        while (os.stat(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs').st_size == 0 and tries < 5):
            try:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', 'wb').write(r.content)
                tries += 1
        # print(f'Balance Sheet for {self.ticker} finished')

    def get_cashflow(self, period=12, number=3):
        url = (f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=cf&period={period}&dataType=A&order=asc&columnYear=5&number={number}')
        r = requests.get(url)
        open(f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', 'wb').write(r.content)
        # while error until it works.
        tries = 0
        while (os.stat(f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs').st_size == 0) and tries < 5:
            try:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', 'wb').write(r.content)
                tries += 1
        # print(f'Cash Flow Statement for {self.ticker} finished')

    def download_all_financials(self):
        self.get_keyratios()
        self.get_income()
        self.get_balancesheet()
        self.get_cashflow()

def check_errors():
    print('checking for errors')
    universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))
    delete_count = 0
    # checking for folders that should not exist anymore.
    for root, dirs, files in os.walk('data/CompanyData/'):
        ticker = root[17:]
        if ticker not in universe:
            if ticker != '':
                delete_count += 1
                shutil.rmtree(root)
                print(ticker, f' not in universe and {root} is deleted')
    # checking for empty files.
    empty_count = 0
    for root, dirs, files in os.walk('data/CompanyData/'):
        for file in files:
            if os.stat(f'{root}/{file}').st_size == 0:
                # Try to download the file again.
                isin = universe[ticker][0]  # get the isin from pickle
                ticker = root[17:]
                company = CompanyFinancialData(ticker, isin)
                company.make_dir(update=True)
                # still empty
                if os.stat(f'{root}/{file}').st_size == 0:
                    empty_count += 1
                    print(f"Error: {file} is an empty file.")

    print('Total deleted folders ', delete_count)
    print("Total empty file errors ", empty_count)
    print(f"Finished error checking on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

def download_prices(ticker):
    df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=full')
    # df = df[(df.close != 0)]  # drop rows with an error.
    print(df)
    # df.to_csv(f'data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs')  # Save the data

# Download financials for every company. Should be redownloaded once in a while to get latest.
def download_company_financial_data(update=False):
    print('Downloading the financials for every company')
    universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))
    for key, value in universe.items():
        company = CompanyFinancialData(key, value[0])  # ticker, isin
        company.make_dir(update=update)
    print(f"finished getting the updated financials on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

# Downloading stock prices for all companies (up to 20 years of daily price)
def all_stock_prices():
    while True:
        print('Downloading all stocks historical prices.')
        universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))  # keeps on opening it again, so it's always using updated data.
        for key_ticker, value in universe.items():
            download_prices(key_ticker)
            print(key_ticker, ': finished downloding stock prices')
            time.sleep(12)  # max 5 requests every minute
        print(f"All stocks prices updated on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

def calc_pe_avgs():
    universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))
    print(universe)
    for key_ticker, value in universe.items():
        name = value[1]
        isin = value[0]
        sector = value[3]
        stock_currency = value[2]

        stock = usedata.Stock(key_ticker, name, isin, sector, stock_currency)
        stock.get_pe_ratio(eps)  # get EPS!!
    # for every company
    # ROA, ROE, ROIC, Gross margin, operating margin, revenue growth yoy, P/E, financial leverage, interest coverage etc.
    # if data don't exist pass
    # dictionary with all avgs.
    # get value from a company add it to total


def download_indecies():
    # first get list of companies in said index and save it to a pickle
    # have a dictionary for all indecies and their ticker
    ticker = 'OMXC25'
    df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=full')
    print(df)


if __name__ == "__main__":
    args = sys.argv
    # command line command to show what to download.
    if args[1] == "financials":
        # **** Running the list of companies on Nasdaq Copenhagen. Should be updated once a week to get changes.
        while True:
            print('Getting the list of companies from Nasdaq CPH')
            save_nasdaqcph_companies()
            # # **** Downloading the financials for every company. Should be redownloaded once in a while to get latest.
            print('Downloading the financials for every company')
            download_company_financial_data(True)  # if True then update all.
            # **** Check for errors and retry all companies with errors
            check_errors()  # check how many errors still exist after trying again. Files that still error don't exist.
            # Calculate market averages on key ratios
            calc_market_avgs()
            # Calculate sector averages on key ratios
            time.sleep(604800)  # sleeps for a week
    elif args[1] == "prices":
        # **** Getting the stocks historical prices.
        all_stock_prices()  # keeps on getting the newest stock prices for all stocks.
    else:
        # download_prices('CSE')
        # calc_pe_avgs()
        # print('error in arguments.')
        x = CompanyFinancialData('ACA', 'US0396531008')
        x.make_dir(update=True)
