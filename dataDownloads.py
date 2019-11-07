import bs4 as bs
import pickle
import os
import requests
import pandas as pd
import time
import sys
import shutil
from decimal import Decimal
import usedata
import urllib.request
import json
from settings import APIKEY, APIKEY2, APIKEY3, PATH
# import pp
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
    if not os.path.isdir(f"{PATH}/data"):
        os.mkdir(f"{PATH}/data")
    if not os.path.isdir(f"{PATH}/data/pickles"):
        os.mkdir(f"{PATH}/data/pickles")
    if not os.path.isdir(f"{PATH}/data/CompanyData"):
        os.mkdir(f"{PATH}/data/CompanyData")

    with open(f'{PATH}/data/pickles/universe_companies.pickle', 'wb') as f:   # Dictionary with all companies. key:ticker values:isin, name, currency, sector, icb
        pickle.dump(companies, f, protocol=pickle.HIGHEST_PROTOCOL)

    alternative_list = []
    for ticker in companies:
        ticker = ticker.replace(".CPH", ".CO")
        alternative_list.append(ticker)

    with open(f'{PATH}/data/pickles/universe_companies_alternative.pickle', 'wb') as f:   # list of all stock tickers using the alternative format with the .CO instead of .CPH
        pickle.dump(alternative_list, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(f'{PATH}/data/pickles/search.pickle', 'wb') as f:  # list with lists containing name and ticker.
        pickle.dump(search, f, protocol=pickle.HIGHEST_PROTOCOL)

    # making sure that every company has a directory for its data.
    for key, vals in companies.items():  # key will be the ticker name.
        if not os.path.isdir(f'{PATH}/data/CompanyData/{key}/'):
            os.makedirs(f'{PATH}/data/CompanyData/{key}/')
            print(f"dir for {key} has been made")

    # checking for companies that are not in the market anymore, so their folders should not exist anymore.
    for root, dirs, files in os.walk(f'{PATH}/data/CompanyData/'):
        ticker = root
        while "/" in ticker:
            index = ticker.find("/") + 1
            ticker = ticker[index:]
        print(ticker)
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
        open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', 'wb').write(r.content)
        # Try until it works.
        tries = 0
        while (os.stat(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs').st_size == 0 and tries < 5):
            try:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', 'wb').write(r.content)
                tries += 1

    def get_income(self, period=12, number=3):
        url = f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=is&period={period}&dataType=A&order=asc&columnYear=5&number={number}'
        referer = f"http://financials.morningstar.com/income-statement/is.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
        open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', 'wb').write(r.content)
        # while error try until it works.
        tries = 0
        while (os.stat(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs').st_size == 0 and tries < 5):
            try:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', 'wb').write(r.content)
                tries += 1
        # print(f'Income Statement for {self.ticker} finished')

    def get_balancesheet(self, period=12, number=3):
        url = f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=bs&period={period}&dataType=A&order=asc&columnYear=5&number={number}'
        referer = f"http://financials.morningstar.com/balance-sheet/bs.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
        open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', 'wb').write(r.content)
        # while error try until it works.
        tries = 0
        while (os.stat(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs').st_size == 0 and tries < 5):
            try:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', 'wb').write(r.content)
                tries += 1
        # print(f'Balance Sheet for {self.ticker} finished')

    def get_cashflow(self, period=12, number=3):
        url = f'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t={self.isin}&reportType=cf&period={period}&dataType=A&order=asc&columnYear=5&number={number}'
        referer = f"http://financials.morningstar.com/cash-flow/cf.html?t={self.isin}"
        r = requests.get(url, headers={"referer": referer})
        open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', 'wb').write(r.content)
        # while error until it works.
        tries = 0
        while (os.stat(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs').st_size == 0) and tries < 5:
            try:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', 'wb').write(r.content)
                tries += 1
            except requests.exceptions.ReadTimeout:
                r = requests.get(url, timeout=1)
                open(f'{PATH}/data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', 'wb').write(r.content)
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
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    # checking for empty files.
    empty_count = 0
    for root, dirs, files in os.walk(f'{PATH}/data/CompanyData/'):
        for file in files:
            if os.stat(f'{PATH}/{root}/{file}').st_size == 0:
                # Try to download the file again.
                ticker = root[17:]
                isin = universe[ticker][0]  # get the isin from pickle
                company = CompanyFinancialData(ticker, isin)
                company.download_all_financials()
                # still empty then just delete the file. (error in morning stars data or in my search)
                if os.stat(f'{PATH}/{root}/{file}').st_size == 0:
                    os.remove(f'{PATH}/{root}/{file}')
                    empty_count += 1
                    print(f"Error: {file} is an empty file.")

    print("Total empty file errors ", empty_count)
    print(f"Finished error checking on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

def download_prices(ticker):
    print(f"Downloading stock prices for {ticker}")
    try:  # try getting the full dataset (in new API update this almost never works anymore)
        df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=full')
    except urllib.error.URLError:  # if there's a request error let's try again
        df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY2}&datatype=csv&outputsize=full')
    if "Error" in df.iloc[0][0] or "Note" in df.iloc[0][0]:  # if there's an error in the returned data then let's try one more time.
        # let's try again
        time.sleep(1)
        df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=full')
        if "Error" in df.iloc[0][0] or "Note" in df.iloc[0][0]:  # There's an error again, so Let's get the compact data (last 100 days) instead and then add it on top of the existing historical data.
            time.sleep(5)
            df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY2}&datatype=csv&outputsize=compact')
            if "Error" in df.iloc[0][0] or "Note" in df.iloc[0][0]:  # There's an error, let's try again.
                time.sleep(10)
                df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=compact')
                if "Error" in df.iloc[0][0] or "Note" in df.iloc[0][0]:  # Keeps up getting an error. We can't retrieve this data.
                    print(f"giving up on getting data for {ticker}")
            else:  # We got the compact data without an error, so let's now add the new data on top of the existing historical data.
                try:
                    df_old = pd.read_csv(f'{PATH}/data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
                except FileNotFoundError:  # except if there's not already any data (probably a new company) then let's just get the last 100 days.
                    df = pd.read_csv(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&datatype=csv&outputsize=compact')
                    df.set_index('timestamp', inplace=True)
                    if "Error" in df.iloc[0][0] or "Note" in df.iloc[0][0]:  # if we can't get this data then pass
                        return False
                df_old.set_index('timestamp', inplace=True)
                if "Unnamed: 0" in df_old.columns:
                    df_old.drop("Unnamed: 0", axis=1, inplace=True)
                last_date = df_old.index[0]
                if df.index.name != "timestamp":
                    df.set_index('timestamp', inplace=True)
                merge_date = list(df.index).index(last_date)
                new_data = df.iloc[:merge_date]
                df = pd.concat([new_data, df_old])
        else:  # There was no error and let's prepare the data by setting the index.
            if df.index.name != "timestamp":
                df.set_index('timestamp', inplace=True)
    else:  # There was no error and let's prepare the data by setting the index.
        if df.index.name != "timestamp":
            df.set_index('timestamp', inplace=True)
    df = df[(df.close != 0)]  # drop rows with errors
    df.to_csv(f'{PATH}/data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs')  # Saving the data
    return True

def download_prices_alternative(ticker):
    ticker_alternative = ticker.replace(".CPH", ".CO")
    # print(f"Getting prices for {ticker}")
    if ticker_alternative == "GMAB.CO":
        download_prices(ticker)
    else:
        df = pd.read_csv(f"https://api.worldtradingdata.com/api/v1/history?symbol={ticker_alternative}&api_token={APIKEY3}&sort_order=oldest&output=csv")
        if "Error" in df.columns[0]:
            download_prices(ticker)
        else:
            # print(df.head())
            df.columns = ['timestamp', 'open', 'close', 'high', 'low', 'volume']
            df.set_index('timestamp', inplace=True)
            df.to_csv(f'{PATH}/data/CompanyData/{ticker}/{ticker}_DailyPrices.cvs')  # Saving the data
            return True

# Download financials for every company. Should be redownloaded once in a while to get latest.
def download_company_financial_data():
    print(f"Starting to download all financial data for each company at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    n = 0
    universe_size = len(universe)
    for key, value in universe.items():
        n += 1
        company = CompanyFinancialData(key, value[0])  # ticker, isin. Creating a company object.
        company.download_all_financials()  # downloading the financials.
        print(f"Finished downloading financial data for {key}. {n} out of {universe_size} at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    print(f"finished getting downloading all financials on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

# Downloading stock prices for all companies (up to 20 years of daily prices)
def all_stock_prices():
    print(f"Starting to download all stocks prices at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    n = 0
    universe_size = len(universe)
    errors = []
    for key_ticker, value in universe.items():
        n += 1
        if download_prices_alternative(key_ticker):
            print(f"Stock prices for {key_ticker} are finished downloading. {n} out of {universe_size} at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
        else:
            print(f"Error getting stock prices for {key_ticker}")
            errors.append(key_ticker)

    for ticker in errors:
        if download_prices_alternative(key_ticker):
            print(f"Stock prices for {key_ticker} are finished downloading. {n} out of {universe_size} at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
        else:
            print(f"Error getting stock prices for {key_ticker}. Going to get it from another source.")
            # Let's try using another API
            if download_prices(key_ticker):
                print(f"Stock prices for {key_ticker} are finished downloading. {n} out of {universe_size} at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
                time.sleep(12)  # max 5 requests every minute
            else:
                print(f"can't get prices for {key_ticker}")
    print(f"All stocks prices updated on {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")

# Updates the pickle with the descriptive data for all stocks.
# def update_descriptive_data():
    # get the data

    # should include the following: Market cap, sector, Volume, Share price, Stock exchange, currency, shares outstanding

def calculate_average_keyratios():  # calculates average key ratios for the whole market and each sector.
    # create pickle file called average_keyratios.pickle where all of the average key ratios are saved

    if not os.path.isfile(f"{PATH}/data/pickles/average_keyratios.pickle"):  # if the file doesn't exist then let's create it.
        average_keyratios = {}
    else:
        average_keyratios = pickle.load(open(f"{PATH}/data/pickles/average_keyratios.pickle", "rb"))

    if not os.path.isfile("data/pickles/sector_average_keyratios.pickle"):  # if the file doesn't exist then let's create it.
        sector_average_keyratios = {}
    else:
        sector_average_keyratios = pickle.load(open(f"{PATH}/data/pickles/sector_average_keyratios.pickle", "rb"))

    for root, dirs, files in os.walk(f"{PATH}/data/pickles/"):
        for file in files:
            if "_data" in file:
                old_data = pickle.load(open(f'{PATH}/data/pickles/{file}', "rb"))
                ratio_category = file[:-7]
                for ratio, values in old_data.items():
                    sum_values = 0
                    n = 0
                    for company_ticker, value in values.items():
                        sum_values += Decimal(str(value[0]).replace(",", "."))
                        n += 1
                        sector_name = value[1][2]
                        if sector_name in sector_average_keyratios:  # if the sector's name is in the data then store the data in there, else create a new key for the sector
                            if ratio_category in sector_average_keyratios[sector_name]:  # if the ratio category exists
                                if ratio in sector_average_keyratios[sector_name][ratio_category]:  # if the ratio exists then store the data in there
                                    sector_average_keyratios[sector_name][ratio_category][ratio]["values"].update({company_ticker: str(value[0]).replace(",", ".")})
                                else:  # the ratio is not in the data.
                                    sector_average_keyratios[sector_name][ratio_category].update({ratio: {"values": {company_ticker: str(value[0]).replace(",", ".")}}})
                            else:  # the ratio category is not in the data
                                sector_average_keyratios[sector_name].update({ratio_category: {ratio: {"values": {company_ticker: str(value[0]).replace(",", ".")}}}})
                        else:  # sector's name is not in the data, so let's add it.
                            sector_average_keyratios.update({sector_name: {ratio_category: {ratio: {"values": {company_ticker: str(value[0]).replace(",", ".")}}}}})

                    avg_ratio = float(sum_values / n)  # calculating market avg key ratios
                    if ratio_category in average_keyratios:  # if the category does not already exist in the file then add it
                        average_keyratios[ratio_category].update({ratio: [avg_ratio, n]})
                    else:
                        average_keyratios.update({ratio_category: {ratio: [avg_ratio, n]}})

    with open(f'{PATH}/data/pickles/average_keyratios.pickle', 'wb') as f:  # saving market averages
        pickle.dump(average_keyratios, f, protocol=pickle.HIGHEST_PROTOCOL)

    sector_average_keyratios = duplicate_data_sector(sector_average_keyratios)

    for sector in sector_average_keyratios:
        for category in sector_average_keyratios[sector]:
            for ratio in sector_average_keyratios[sector][category]:
                sum_values = 0
                n = 0
                for ticker, value in sector_average_keyratios[sector][category][ratio]["values"].items():
                    sum_values += Decimal(value)
                    n += 1
                avg_ratio = float(sum_values / n)  # calculating sector avgs
                sector_average_keyratios[sector][category][ratio].update({"results": [avg_ratio, n]})
    with open(f'{PATH}/data/pickles/sector_average_keyratios.pickle', 'wb') as f:  # saving sector averages
        pickle.dump(sector_average_keyratios, f, protocol=pickle.HIGHEST_PROTOCOL)

def duplicate_data_sector(sector_average_keyratios):  # check if a company's data is in multiple sectors. (this will happen if a company has changed sectors)
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    delete_list = list()
    for universe_ticker, universe_values in universe.items():
        for sector in sector_average_keyratios:
            for category in sector_average_keyratios[sector]:
                for ratio in sector_average_keyratios[sector][category]:
                    for ticker, value in sector_average_keyratios[sector][category][ratio]["values"].items():
                        if ticker.upper() == universe_ticker.upper() and sector.upper() != universe_values[3].upper():  # if company is in this sectors data and company's sector is not the same the delete the data
                            delete_list.append([ticker, ratio, category, sector])
    for delete_info in delete_list:
        sector_average_keyratios[delete_info[3]][delete_info[2]][delete_info[1]]["values"].pop(delete_info[0])
        if not bool(sector_average_keyratios[delete_info[3]][delete_info[2]][delete_info[1]]["values"]):  # if this is the only value in "values" key delete the whole ratio as the data doesn't exist anymore and should the average should not be calculated.
            sector_average_keyratios[delete_info[3]][delete_info[2]].pop(delete_info[1])
        if not bool(sector_average_keyratios[delete_info[3]][delete_info[2]]):  # if there's no values in a category then the category should be deleted.
            sector_average_keyratios[delete_info[3]].pop(delete_info[2])
        if not bool(sector_average_keyratios[delete_info[3]]):  # if there's no values in sector then the sector should be deleted.
            sector_average_keyratios.pop(delete_info[3])
    return sector_average_keyratios

def check_errors_keyratios_data():
    keyratios_file_names = {"rev_growth_data", "inc_growth_data", "efficiency_data", "financials_data", "profitability_data", "cashflow_data", "liquidity_data"}
    # let's check for stocks that are not in our universe and delete them.
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    for pickle_name in keyratios_file_names:
        # open the pickle for a category of key ratios
        new_data = pickle.load(open(f"{PATH}/data/pickles/{pickle_name}.pickle", "rb"))
        old_data = pickle.load(open(f"{PATH}/data/pickles/{pickle_name}.pickle", "rb"))
        for ratio in old_data:  # for each ratio in the pickle file check through the tickers
            for ticker in old_data[ratio]:  # for each ticker within each ratio check if the ticker is in the universe if not then delete it.
                if ticker in universe:  # the ticker is in the universe we don't have to do anything
                    pass
                else:  # ticker is not in the universe, so let's delete it.
                    del new_data[ratio][ticker]
        # saving the updated pickle file
        with open(f'{PATH}/data/pickles/{pickle_name}.pickle', 'wb') as f:
            pickle.dump(new_data, f, protocol=pickle.HIGHEST_PROTOCOL)

# updates the _data pickle files with key ratios for all stocks and then updates the calculated average market and sector of each key ratio.
def get_all_keyratios_avgs():
    print(f"Calculating all key ratios average for both market and each sector at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    for ticker, values in universe.items():
        print(f"Saving key ratios for {ticker}")
        stock = usedata.Stock(ticker, values[1], values[0], values[3], values[2])  # ticker, name, isin, sector, stock_currency
        stock.save_keyratios()
    check_errors_keyratios_data()
    calculate_average_keyratios()
    print(f"Finished calculating key ratios averages at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")


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
            # # # **** Downloading the financials for every company. Should be redownloaded once in a while to get latest.
            download_company_financial_data()  # if True then update all, otherwise only new companies in the market.
            # # Check for errors and retry all companies with errors
            check_errors()  # check how many errors still exist after trying again. Files that still error don't exist.
            get_all_keyratios_avgs()  # updates the pickle files for all stocks and then updates the calculated average market and sector of each key ratio.

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
            save_nasdaqcph_companies()  # first this one to run
            # all_stock_prices()
            # download_company_financial_data()
            get_all_keyratios_avgs()  # last to run after all the others are finished
            print(f"finished setting up application at {time.strftime('%d/%m/%Y')} at {time.strftime('%H:%M:%S')}")
        elif args[1] == "test":
            print("testing new function on a single company")
            ticker = "VWS.CPH"
            isin = "DK0010268606"
            company = CompanyFinancialData(ticker, isin)  # ticker, isin. Creating a company object.
            company.download_all_financials()  # downloading the financials.
        elif "ticker" in args[1]:  # updates latest stock prices for specific company
            ticker = args[1][7:].upper()
            print(ticker)
            # download_prices(ticker)
            download_prices_alternative(ticker)
        else:
            print('Use an argument to run specific functions.')
            print('"update financials" downloads the financial data for all companies.')
            print('"update prices" downloads the stock prices for all companies.')
            print('"update universe" downloads the NASDAQ Copenhagen.')
            print('"setup" for first time use. Downloading all of the above')
            print('"test" for testing new functions')
            print("'ticker {ticker}' for updating prices for ticker")

            stock = usedata.Stock("SAS-DKK.CPH", "name", "isin", "sector", "stock_currency")  # ticker, name, isin, sector, stock_currency
            stock.save_keyratios()
    end = time.time()
    run_time_s = end - start
    run_time_m = run_time_s / 60
    print(f'time: {run_time_s} Seconds or {run_time_m} Minutes')


# 2019-06-13 last date
