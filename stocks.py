import requests
import pandas as pd
import pickle
import datetime as dt

class stock_analysis(object):
    def __init__(self, ticker, isin, name, sector, icb, apikey):
        self.ticker = ticker
        self.isin = isin
        self.name = name
        self.sector = sector
        self.icb = icb
        self.apikey = apikey
        self.today = dt.date.today()
        self.price_days_ago = [7, 14, 30, 60, 90, 180, 365, 730, 1095, 1825]  # 1w, 2w, 1m, 2m, 3m, 6m, 1y, 2y, 3y, 5y

    def open_data(self):
        # Key Ratios
        df_kr_revenue = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=0, skip_blank_lines=True, index_col=[0], skiprows=range(0, 42), nrows=5)
        revenue_growth_yoy = df_kr_revenue.loc['Year over Year']
        self.revenue_growth_yoy = revenue_growth_yoy.todict()

        revenue_growth_3y = df_kr_revenue.loc['3-Year Average']
        self.revenue_growth_3y = revenue_growth_3y.todict()

        revenue_growth_5y = df_kr_revenue.loc['5-Year Average']
        self.revenue_growth_5y = revenue_growth_5y.todict()

        revenue_growth_10y = df_kr_revenue.loc['10-Year Average']
        self.revenue_growth_10y = revenue_growth_10y.todict()

        df_kr_revenue = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=0, skip_blank_lines=True, index_col=[0], skiprows=range(0, 42), nrows=5)
        # Income statement
        df_is = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0])
        df_is.drop(["Operating expenses", "Earnings per share", "Weighted average shares outstanding"], inplace=True)

        duplicates = df_is.index.duplicated(keep='last')
        num = 0
        dups_id = []
        for x in duplicates:
            if x:
                dups_id.append(num)
            num += 1

        # Earnings per share
        eps_basic = df_is.iloc[dups_id[0]]
        self.eps_basic = eps_basic.to_dict()

        eps_diluted = df_is.iloc[dups_id[1]]
        self.eps_diluted = eps_diluted.to_dict()

        # Weighted average shares outstanding
        outstanding_shares_basic = df_is.iloc[dups_id[1] + 1]
        self.outstanding_shares_basic = outstanding_shares_basic.todict()

        outstanding_shares_diluted = df_is.iloc[dups_id[1] + 2]
        self.outstanding_shares_diluted = outstanding_shares_diluted.todict()

        revenue = df_is.loc['Revenue']
        self.revenue = revenue.to_dict()

        earnings = df_is.loc['Net income']
        self.earnings = earnings.to_dict()

        ebit = df_is.loc['Operating income']
        self.ebit = ebit.to_dict()

        # Balance Sheet
        df_bs = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0])

        common_shares = df_bs.loc['Common stock']
        self.common_shares = common_shares.to_dict()

        # Cash flow
        # df_cf = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0])

    def get_stock_price(self, download=False):  # daily adjusted close price (up to 20 years)
        if download:
            # Downloading stock prices
            url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={self.ticker}&apikey={self.apikey}&datatype=csv&outputsize=full')
            r = requests.get(url)
            open(f'data/CompanyData/{self.ticker}/{self.ticker}_DailyPrices.cvs', 'wb').write(r.content)
        df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_DailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
        df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])
        df_price.set_index('timestamp', inplace=True)
        past_prices = {}  # saving prices in a dict
        # Getting the latest price
        price_latest = (df_price['adjusted_close'][0])
        if price_latest == 0:
            attempt = 1
            while price_latest == 0 and attempt < 5:  # if market is closed this day go to latest open day.
                price_latest = (df_price['adjusted_close'][attempt])
                attempt += 1
            if attempt == 5:
                price_latest = 0
        past_prices['Current'] = price_latest  # Saving to dict

        # Function getting a date x days ago.
        def time_ago(time):
            time_ago = self.today - dt.timedelta(days=time)
            return time_ago
        # List of prices we want.
        for days_ago in self.price_days_ago:
            last_date = df_price.index[-1]
            last_date = last_date.date()
            days_difference = (self.today - last_date).days
            if days_ago > days_difference:
                past_prices[days_ago] = 'NaN'
            else:
                df_price_xdays_ago = df_price.truncate(before=time_ago(days_ago))
                price_xdays_ago = (df_price_xdays_ago['adjusted_close'][0])
                if price_xdays_ago == 0:
                    attempt = 1
                    while price_xdays_ago == 0 and attempt < 5:
                        price_xdays_ago = (df_price_xdays_ago['adjusted_close'][attempt])
                        attempt += 1
                    if attempt == 5:
                        price_xdays_ago = 0
                past_prices[days_ago] = price_xdays_ago
        self.past_prices = past_prices

    def calculations(self):
        # Stock growth since x days ago
        latest_price = self.past_prices['Current']
        price_growth = {'Current': 'NaN'}
        for days_ago, price_xdays_ago in self.past_prices.items():
            if days_ago == 'Current' or price_xdays_ago == 'NaN':
                pass
            else:
                growth = ((latest_price - price_xdays_ago) / price_xdays_ago) * 100
                price_growth[days_ago] = growth
        self.price_growth = price_growth

        # P/E Ratio: Price per share / EPS
        self.PE = latest_price / self.eps_diluted['TTM']

    def sector(self):
        pass

    def save_calcs(self):
        pass
        # stock key ratios
        # index = ['Past prices', 'Price growth']
        # all_calcs_stock = pd.DataFrame([self.past_prices, self.price_growth], index=index)
        # # financial key ratios
        # index = ['EPS Diluted']
        # all_calcs_financial = pd.DataFrame([self.eps_diluted, ], index=index)
        # # avg. sector key ratios
        # index = []
        # all_calcs_sector = pd.DataFrame([], index=index)

    def download_all(self, download=False):
        self.open_data()
        self.get_stock_price(download=download)
        self.calculations()
        # self.save_calcs()


def analyse_all(apikey, download=False):
    universe = pickle.load(open('pickles/universe_companies.pickle', 'rb'))
    for key, value in universe.items():
        stock = stock_analysis(key, value[0], value[1], value[3], value[4], apikey)  # name, isin, ticker, sector, icb, apikey
        stock.download_all(download=download)
        print(key, ' is finished')


# def individual_analysis(ticker):
#     universe = pickle.load(open('pickles/universe_companies.pickle', 'rb'))
#     ticker_values = universe[ticker]


if __name__ == "__main__":
    # save_nasdaqcph_companies()
    # download_company_data()
    # check_empty_data()
    analyse_all(True)

    # individual_analysis('DLH.CO')

    # AaB_stock = stock_analysis('DLH.CO', 'DK0060868966', 'DLH', '', '5700', apikey)
    # AaB_stock.download_all()

    # save_nasdaqcph_companies()

    # download_company_data(True)  # put argument to True if you want to update all the existing data.

    # check_empty_data()  # only checks income, balance, cashflow & keyratios.

    # analyse_all()  # put argument to True if you want to download all the data for the first time.
