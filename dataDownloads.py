import bs4 as bs
import pickle
import os
import requests
import pandas as pd
import time
import sys
import shutil
from usedata import get_all_keyratios_avgs
from settings import APIKEY

# The list of companies on Nasdaq Copenhagen. Should be updated once in a while to get changes.
def save_nasdaqcph_companies():
    # getting list of all the listed companies
    print(f"Starting to get all companies ticker data in NASDAQ CPH at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    r = requests.get('http://www.nasdaqomxnordic.com/aktier/listed-companies/copenhagen', timeout=10)
    soup = bs.BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', {'id': 'listedCompanies'})
    companies = {}
    search = []
    for row in table.findAll('tr')[1:]:
        name = row.findAll('td')[0].text
        ticker = row.findAll('td')[1].text

        mapping_ticker = str.maketrans(' ', '-')   # changing the tickers to have same format.
        ticker = ticker.translate(mapping_ticker)
        ticker = ticker + '.CPH'

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

    # creating the directories if they don't exist
    if not os.path.isdir("data"):
        os.mkdir("data")
    if not os.path.isdir("data/pickles"):
        os.mkdir("data/pickles")

    with open('data/pickles/universe_companies.pickle', 'wb') as f:   # Dictionary with all companies. key:ticker values:isin, name, currency, sector, icb
        pickle.dump(companies, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('data/pickles/search.pickle', 'wb') as f:  # list with lists containing name and ticker.
        pickle.dump(search, f, protocol=pickle.HIGHEST_PROTOCOL)

    # making sure that every company has a directory for its data.
    for key, vals in companies.items():  # key will be the ticker name.
        if not os.path.isdir(f'data/CompanyData/{key}/'):
            os.makedirs(f'data/CompanyData/{key}/')
            print(f"dir for {key} has been made")

    # checking for companies that are not in the market anymore, so their folders should not exist anymore.
    for root, dirs, files in os.walk('data/CompanyData/'):
        ticker = root[17:]
        if ticker not in companies:
            if ticker != '':
                shutil.rmtree(root)
                print(ticker, f' not in universe and {root} is deleted')

    print(f"finished getting the updated tickers for NASDAQ CPH on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

class CompanyFinancialData(object):
    def __init__(self, ticker, isin):
        self.ticker = ticker
        self.isin = isin

    def get_keyratios(self):
        url = f'http://financials.morningstar.com/ajax/exportKR2CSV.html?t={self.isin}'
        referer = f"http://financials.morningstar.com/ratios/r.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
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

    def get_income(self, period=12, number=3):
        url = f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=is&period={period}&dataType=A&order=asc&columnYear=5&number={number}'
        referer = f"http://financials.morningstar.com/income-statement/is.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
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
        url = f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=bs&period={period}&dataType=A&order=asc&columnYear=5&number={number}'
        referer = f"http://financials.morningstar.com/balance-sheet/bs.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
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
        url = f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=cf&period={period}&dataType=A&order=asc&columnYear=5&number={number}'
        referer = f"http://financials.morningstar.com/cash-flow/cf.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
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

# checking for some basics error. First, deleting companies that are not on the stock market anymore. Secondly, checking for empty files meaning that they don't exist in Morningstars database.
def check_errors():
    print('checking for errors')
    universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))
    # checking for empty files.
    empty_count = 0
    for root, dirs, files in os.walk('data/CompanyData/'):
        for file in files:
            if os.stat(f'{root}/{file}').st_size == 0:
                # Try to download the file again.
                ticker = root[17:]
                isin = universe[ticker][0]  # get the isin from pickle
                company = CompanyFinancialData(ticker, isin)
                company.download_all_financials()
                # still empty then just delete the file. (error in morning stars data or in my search)
                if os.stat(f'{root}/{file}').st_size == 0:
                    os.remove(f'{root}/{file}')
                    empty_count += 1
                    print(f"Error: {file} is an empty file.")

    print("Total empty file errors ", empty_count)
    print(f"Finished error checking on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

def download_prices(ticker):
    try:
        df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=full')
    except urllib.error.HTTPError:
        time.sleep(5)
        df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=full')
    # df = df[(df.close != 0)]  # drop rows with an error.
    # print(df)
    df.to_csv(f'data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs')  # Save the data

# Download financials for every company. Should be redownloaded once in a while to get latest.
def download_company_financial_data():
    print(f"Starting to download all financial data for each company at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))
    n = 0
    universe_size = len(universe)
    for key, value in universe.items():
        n += 1
        company = CompanyFinancialData(key, value[0])  # ticker, isin. Creating a company object.
        company.download_all_financials()  # downloading the financials.
        print("Finished downloading financial data for {key}. {n} out of {universe_size} at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    print(f"finished getting downloading all financials on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

# Downloading stock prices for all companies (up to 20 years of daily prices)
def all_stock_prices():
    print(f"Starting to download all stocks prices at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))
    n = 0
    universe_size = len(universe)
    for key_ticker, value in universe.items():
        n += 1
        download_prices(key_ticker)
        print(f"Stock prices for {key_ticker} are finished downloading. {n} out of {universe_size} at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
        time.sleep(12.1)  # max 5 requests every minute
    print(f"All stocks prices updated on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

def setup():
    save_nasdaqcph_companies()  # first this one to run
    all_stock_prices()
    download_company_financial_data()
    get_all_keyratios_avgs()  # last to run after all the others are finished


if __name__ == "__main__":
    args = sys.argv
    start = time.time()
    if len(args) == 1:
        print('Use an argument to run specific functions.')
        print('"update financials" downloads the financial data for all companies.')
        print('"update prices" downloads the stock prices for all companies.')
        print('"update universe" downloads the NASDAQ Copenhagen.')
        print('"setup" for first time use. Downloading all of the above')
        print('"test" for testing new functions')
    else:
        if args[1] == "update financials":
            print("updating financial data for all companies")
            save_nasdaqcph_companies()  # updating the list of companies on the market.
            # # **** Downloading the financials for every company. Should be redownloaded once in a while to get latest.
            download_company_financial_data()  # if True then update all, otherwise only new companies in the market.
            # Check for errors and retry all companies with errors
            check_errors()  # check how many errors still exist after trying again. Files that still error don't exist.

        elif args[1] == "update prices":
            # **** Getting the historical prices of all stocks.
            print("updating prices for all stocks")
            save_nasdaqcph_companies()  # updating the list of companies on the market.
            all_stock_prices()  # keeps on getting the newest stock prices for all stocks.
        elif args[1] == "update universe":
            print("updating NASDAQ Copenhagen list of companies")
            save_nasdaqcph_companies()  # updating the list of companies on the market.
        elif args[1] == "setup":
            print(f"setting up application for first time use at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
            setup()
            print(f"finished setting up application at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
        elif args[1] == "test":
            print("testing new function on a single company")
            ticker = "VWS.CPH"
            isin = "DK0010268606"
            company = CompanyFinancialData(ticker, isin)  # ticker, isin. Creating a company object.
            company.download_all_financials()  # downloading the financials.
        else:
            print('Use an argument to run specific functions.')
            print('"update financials" downloads the financial data for all companies.')
            print('"update prices" downloads the stock prices for all companies.')
            print('"update universe" downloads the NASDAQ Copenhagen.')
            print('"setup" for first time use. Downloading all of the above')
            print('"test" for testing new functions')
    end = time.time()
    run_time_s = end - start
    run_time_m = run_time_s / 60
    print(f'time: {run_time_s} Seconds or {run_time_m} Minutes')
