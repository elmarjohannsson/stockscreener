import pandas as pd
import pickle
import os
import datetime as dt
import pp
import time
import urllib.request
import json
from settings import APIKEY

class Stock(object):
    def __init__(self, ticker, name, isin, sector, stock_currency):
        self.ticker = ticker.upper()
        self.name = name
        self.isin = isin
        self.sector = sector
        self.stock_currency = stock_currency
        self.today = dt.date.today()
        self.use_data = self.most_recent_data()  # "daily" or "adj"
        self.past_prices_close = self.historical_stock_price_close()

    def most_recent_data(self):
        if os.path.isfile(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs') and os.path.isfile(f'data/CompanyData/{self.ticker}/{self.ticker}_DailyPrices.cvs'):  # Finding the one with the most recent data
            daily_adj_mtime = os.path.getmtime(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs')
            daily_mtime = os.path.getmtime(f'data/CompanyData/{self.ticker}/{self.ticker}_DailyPrices.cvs')
            if daily_mtime > daily_adj_mtime:
                return "daily"
            elif daily_mtime < daily_adj_mtime:
                return "adj"
            else:
                return "adj"
        elif os.path.isfile(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs'):
            return "adj"
        elif os.path.isfile(f'data/CompanyData/{self.ticker}/{self.ticker}_DailyPrices.cvs'):
            return "daily"
    # Opens the whole balance sheet file

    def open_balance(self):
        # Returns the company's balance sheet as a cvs file
        df_balance = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0], error_bad_lines=False)
        df_balance.fillna('*', inplace=True)
        return df_balance

    # From key ratios it gets Revenue, Gross Margin, Operating Income, Operating Margin and Net Income.
    def open_income(self):
        df_income = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0], error_bad_lines=False)
        df_income.fillna('*', inplace=True)
        return df_income

    def get_income(self):
        # Reads a company's KeyRatios.cvs to find their revenue, gross margin, operating income, operating margin and net income. This gets returns as multiple variables. Each variable is a pandas data series.
        df_revenue = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=0, skip_blank_lines=True, index_col=[0], skiprows=range(0, 2), nrows=5)
        df_revenue.fillna('*', inplace=True)
        revenue = df_revenue.iloc[0]
        grossMargin = df_revenue.iloc[1]
        operatingIncome = df_revenue.iloc[2]
        operatingMargin = df_revenue.iloc[3]
        netIncome = df_revenue.iloc[4]
        return revenue, grossMargin, operatingIncome, operatingMargin, netIncome  # returns as a pandas Series.

    # From the balance sheet it gets total assets and liabilities.
    def get_balance(self):
        # Returns the total assets and liabilities values from the balance sheet as pandas series' ####
        df_balance = self.open_balance()
        assets = df_balance.loc['Total assets']
        liabilities = df_balance.loc['Total liabilities']
        return assets, liabilities  # returns as a pandas Series.

    # Opens the cash flow statement
    def open_cashflow(self):
        # Returns the company's cash flow as a cvs file ###
        cf_url = f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs'
        # if cash flow is not empty then get it
        if not os.path.isfile(cf_url):
            df_cashflow = "*"
        elif os.stat(cf_url).st_size == 0:
            df_cashflow = "*"
        else:
            df_cashflow = pd.read_csv(cf_url, delimiter=',', header=1, skip_blank_lines=True, index_col=[0])
            df_cashflow.fillna('*', inplace=True)
        return df_cashflow

    # From the cash flow statement it gets value of operating, investing and financing activities.
    def get_cashflow(self):
        # Returns the values of investing activities, financing activities and operating activities as pandas series' ####
        df_cashflow = self.open_cashflow()
        investing = df_cashflow.loc['Net cash used for investing activities']
        financing = df_cashflow.loc['Net cash provided by (used for) financing activities']
        try:
            operating = df_cashflow.loc['Net cash provided by operating activities']
        except KeyError:
            try:
                operating = df_cashflow.loc['Operating cash flow']
            except KeyError:
                operating = None
        return operating, investing, financing  # returns as pandas series'.

    # From Key ratios sheet it gets EPS, payout ratio, book value per share, free cash flow and free cash flow per share.
    def get_financials(self):  # Returns financial values by opening the company's key ratios sheet and searching for wanted values ####
        df_financials = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=15)
        df_financials.fillna('*', inplace=True)
        eps = df_financials.iloc[5]
        payout_ratio = df_financials.iloc[7]
        book_value_per_share = df_financials.iloc[9]
        free_cash_flow = df_financials.iloc[12]
        free_cash_flow_per_share = df_financials.iloc[13]
        return eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share

    def check_currency_match(self, ratio):
        if self.stock_currency in ratio.name:  # check if stock price and EPS price are the same
            price_matched = self.past_prices_close["Current"]

        else:  # stock price and EPS price are the same, so we have to get the exchange rate and calculate it.
            if "EUR" in ratio.name:
                to_currency = "EUR"
            elif "USD" in ratio.name:
                to_currency = "USD"
            elif "GBP" in ratio.name:
                to_currency = "GBP"
            elif "SEK" in ratio.name:
                to_currency = "SEK"
            else:
                price_matched = "*"
                return price_matched

            def update_currency(currency_data):  # updates currency and returns current fx
                fx_data = urllib.request.urlopen(f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={self.stock_currency}&to_currency={to_currency}&apikey={APIKEY}')
                fx_data = json.loads(fx_data.read())
                fx = float(fx_data["Realtime Currency Exchange Rate"]['5. Exchange Rate'])
                currency_data[f"{self.stock_currency}to{to_currency}"] = {"Rate": fx, "updated": self.today}
                with open('data/pickles/currencies.pickle', 'wb') as f:   # save exchange rate, so we don't have to get it every time.
                    pickle.dump(currency_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                return fx

            if os.path.isfile("data/pickles/currencies.pickle"):  # check data for currency rate.
                currencies = pickle.load(open('data/pickles/currencies.pickle', 'rb'))
                if f"{self.stock_currency}to{to_currency}" in currencies:  # check if we have for what we need now.
                    days_since_update = self.today - currencies[f"{self.stock_currency}to{to_currency}"]["updated"]
                    if days_since_update > dt.timedelta(5):  # check if the data is too old (5 day) to be used reliably
                        fx = update_currency(currencies)
                    else:
                        fx = currencies[f"{self.stock_currency}to{to_currency}"]["Rate"]
                else:
                    fx = update_currency(currencies)
            else:  # if the file doesn't exist then let's create it.
                currencies = {}
                fx = update_currency(currencies)
            # going from stock_currency (DKK) to (mostly EUR or USD)
            price_matched = self.past_prices_close["Current"] * fx
        return price_matched

    # Calculates P/E ratio: Current price / EPS(ttm)
    def calc_pe_ratio(self, eps):
        # Returns the P/E ratio by getting current price and dividing it with most recent EPS(TTM)
        if self.past_prices_close is not '*':
            if eps[-1] is not '*':   # if EPS or current price does not exist for that year it will return error value.
                price_matched = self.check_currency_match(eps)
                if price_matched != "*":
                    pe = price_matched / float(eps[-1])
                else:
                    pe = "*"
            elif eps[-2] is not '*':  # check if eps for 2nd period exists
                pe = self.past_prices_close['Current'] / float(eps[-2])
            else:
                pe = "*"
        else:
            pe = "*"
        return pe

    # Calculates the debt ratio: total liabilities / total assets
    def calc_debt_ratio(self):
        assets, liabilities = self.get_balance()
        try:
            debt_ratio = liabilities / assets
            return debt_ratio
        except ZeroDivisionError:
            return "*"

    # Calculates the company's Enterprise value: market cap + total borrowing - cash
    def calc_enterprise_value(self):
        shares = self.get_number_of_shares()
        marketcap = self.past_prices_close['Current'] * float(shares['TTM'])
        df_balance = self.open_balance()
        long_term_debt = df_balance.loc['Long-term debt'][-1]
        try:
            short_term_debt = float(df_balance.loc['Short-term debt'][-1])
        except ValueError:  # fix error if data is empty
            short_term_debt = 0.0
        cash = df_balance.loc['Cash and cash equivalents'][-1]
        enterprise_value = marketcap + short_term_debt + long_term_debt - cash
        return enterprise_value

    def calc_avg_volume(self, n):  # n = number of days for avg period
        try:
            df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
        except FileNotFoundError:
            return '*'
        pp(df_price)
        df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])
        df_price.set_index('timestamp', inplace=True)

        sum_volume = 0
        for volume in df_price["volume"].head(n):  # for each data point in the latest n days we find the sum.
            sum_volume += volume

        avg_volume = sum_volume / n  # calculate the average
        return avg_volume

    def get_number_of_shares(self):
        df_keyratios = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=10)
        shares = df_keyratios.loc["Shares Mil"]
        return shares

    def get_all_keyratios(self, result=''):
        try:
            df_kr = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=0, skip_blank_lines=True, index_col=[0], skiprows=range(0, 20))
        except FileNotFoundError:
            return '*'
        df_kr.fillna('*', inplace=True)

        # to get the data from the cvs.
        growth_yoy = df_kr.loc['Year over Year']
        growth_3y = df_kr.loc['3-Year Average']
        growth_5y = df_kr.loc['5-Year Average']
        growth_10y = df_kr.loc['10-Year Average']

        # revenue growth
        revenue_growth_yoy = growth_yoy.iloc[0]  # Returns as a pandas Series
        revenue_growth_3y = growth_3y.iloc[0]
        revenue_growth_5y = growth_5y.iloc[0]
        revenue_growth_10y = growth_10y.iloc[0]
        rev_growth_vals_unsorted = [revenue_growth_yoy, revenue_growth_3y, revenue_growth_5y, revenue_growth_10y]  # combining them to a list
        rev_growth_vals = []
        for val in rev_growth_vals_unsorted:  # Do not add value if only NaN values.
            if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                pass
            else:
                rev_growth_vals.append(val)  # append those that are not only nan values.
        # net income growth
        income_growth_yoy = growth_yoy.iloc[2]
        income_growth_3y = growth_3y.iloc[2]
        income_growth_5y = growth_5y.iloc[2]
        income_growth_10y = growth_10y.iloc[2]
        inc_growth_vals_unsorted = [income_growth_yoy, income_growth_3y, income_growth_5y, income_growth_10y]  # combining them to a list
        inc_growth_vals = []
        for val in inc_growth_vals_unsorted:  # Do not add value if only NaN values.
            if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                pass
            else:
                inc_growth_vals.append(val)  # append those that are not only nan values.
        # Efficiency
        fixed_assets_turnover = df_kr.loc['Fixed Assets Turnover']
        assets_turnover = df_kr.loc['Asset Turnover']
        days_inventory = df_kr.loc['Days Inventory']
        cash_conversion = df_kr.loc['Cash Conversion Cycle']
        inventory_turnover = df_kr.loc['Inventory Turnover']
        efficiency_vals_unsorted = [fixed_assets_turnover, assets_turnover, days_inventory, cash_conversion, inventory_turnover]  # combining them to a list
        efficiency_vals = []
        for val in efficiency_vals_unsorted:  # Do not add value if only NaN values.
            if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                pass
            else:
                efficiency_vals.append(val)  # append those that are not only nan values.
        # Profitibality
        roa = df_kr.loc['Return on Assets %']
        financial_leverage = df_kr.loc['Financial Leverage (Average)']
        roe = df_kr.loc['Return on Equity %']
        roic = df_kr.loc['Return on Invested Capital %']
        interest_coverage = df_kr.loc['Interest Coverage']
        profitability_vals_unsorted = [roa, financial_leverage, roe, roic, interest_coverage]  # combining them to a list
        profitability_vals = []
        for val in profitability_vals_unsorted:  # Do not add value if only NaN values.
            if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                pass
            else:
                profitability_vals.append(val)  # append those that are not only nan values.
        # Cash flow ratios
        cap_ex_sales = df_kr.loc["Cap Ex as a % of Sales"]
        freecashflow_to_sales = df_kr.loc['Free Cash Flow/Sales %']
        cashflow_vals = []
        try:
            freecashflow_to_income = df_kr.loc['Free Cash Flow/Net Income']
            cashflow_vals_unsorted = [cap_ex_sales, freecashflow_to_sales, freecashflow_to_income]  # combining them to a list
            for val in cashflow_vals_unsorted:  # Do not add value if only NaN values.
                if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                    pass
                else:
                    cashflow_vals.append(val)  # append those that are not only nan values.
        # Cash flow ratios
        except KeyError:  # some companies don't have free cash flow to income.
            cashflow_vals_unsorted = [cap_ex_sales, freecashflow_to_sales]  # combining them to a list
            for val in cashflow_vals_unsorted:  # Do not add value if only NaN values.
                if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                    pass
                else:
                    cashflow_vals.append(val)  # append those that are not only NaN values.
        # Liquidity
        current_ratio = df_kr.loc["Current Ratio"]
        quick_ratio = df_kr.loc["Quick Ratio"]
        debt_equity = df_kr.loc["Debt/Equity"]
        liquidity_vals_unsorted = [current_ratio, quick_ratio, debt_equity]  # combining them to a list
        liquidity_vals = []
        for val in liquidity_vals_unsorted:  # Do not add value if only NaN values.
            if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                pass
            else:
                liquidity_vals.append(val)  # append those that are not only nan values.
        # Financials
        eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share = self.get_financials()
        financials_vals_unsorted = [eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share]
        financials_vals = []
        for val in financials_vals_unsorted:  # Do not add value if only NaN values.
            if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                pass
            else:
                financials_vals.append(val)  # append those that are not only nan values.

        return rev_growth_vals, inc_growth_vals, efficiency_vals, financials_vals, profitability_vals, cashflow_vals, liquidity_vals

    def get_valuation_ratios(self):  # right now it only gets the current ratio using the current price. Later I want to add historical as well.
        df_financials = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=15)
        df_financials.fillna('*', inplace=True)
        eps = df_financials.iloc[5]
        pe = self.calc_pe_ratio(eps)
        valuation_vals_unsorted = [pe]
        valuation_vals = []
        for val in valuation_vals_unsorted:  # Do not add value if only NaN values.
            if val == "*":
                pass
            else:
                valuation_vals.append(val)  # append those that are not only nan values.
        # get P/E, dividend yield, price / free cash flow per share, price to book value, price to tangible book value, PEG, price to sales, price to cash flow
        return valuation_vals

    def get_current_price(self):
        try:
            df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
        except FileNotFoundError:
            return '*'
        df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])
        df_price.set_index('timestamp', inplace=True)
        price_latest = (df_price['close'][0])
        return price_latest

    # Function getting a date x days ago.
    def time_ago(self, time):
        time_ago = self.today - dt.timedelta(days=time)
        return time_ago

    # def get_price_specific_date(self, date):  # put in a date and it will return the price on that date if market is closed on that date, we don't have the data and get the most recent before that.
    #     try:
    #         df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
    #     except FileNotFoundError:
    #         return '*'  # maybe we should try download it again.

    def historical_stock_price_close(self):
        if self.use_data == "daily":
            try:
                df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_DailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
            except FileNotFoundError:
                return '*'  # maybe we should try download it again.
            df_price_close = df_price['close']
        elif self.use_data == "adj":
            try:
                df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
            except FileNotFoundError:
                return '*'  # maybe we should try download it again.
            try:
                df_price_close = df_price['adjusted_close']
            except KeyError:
                return "*"
        df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])
        df_price.set_index('timestamp', inplace=True)
        past_prices_close = {}  # saving prices in a dict
        # Getting the latest price
        price_latest = (df_price['close'][0])
        if price_latest == 0:
            attempt = 1
            while price_latest == 0 and attempt < 10:  # if market is closed this day go to latest open day.
                # price_latest = (df_price['adjusted_close'][attempt])
                price_latest = df_price_close[attempt]
                attempt += 1
            if attempt == 10:
                price_latest = 'NaN'  # there is an error with the data.
        self.price_latest = price_latest
        past_prices_close['Current'] = price_latest  # Saving to dict

        price_days_ago = {'1w': 7, '2w': 14, '1m': 30, "2m": 60, '3m': 90, '6m': 180, '1y': 365, '2y': 730, '3y': 1095, '5y': 1825}
        # List of prices we want.
        for key_days_ago, val_days_ago in price_days_ago.items():  # checking the price for all the days ago in the list.
            last_date = df_price.index[-1].date()  # getting the oldest price.
            days_difference = (self.today - last_date).days
            if val_days_ago > days_difference:  # when we have to check a price x days ago, but no price existed at the time.
                past_prices_close[key_days_ago] = 'NaN'
            else:
                df_price_xdays_ago = df_price.truncate(before=self.time_ago(val_days_ago))
                price_xdays_ago = (df_price_xdays_ago['close'][0])
                if price_xdays_ago == 0:
                    attempt = 1
                    while price_xdays_ago == 0 and attempt < 10:
                        price_xdays_ago = (df_price_xdays_ago['close'][attempt])
                        attempt += 1
                    if attempt == 10:
                        price_xdays_ago = 'NaN'
                past_prices_close[key_days_ago] = price_xdays_ago
        return past_prices_close

    def stock_growth(self):
        # Stock growth since x days ago
        if self.past_prices_close == "*":
            price_growth = "*"
        else:
            price_latest = self.past_prices_close['Current']
            price_growth = {}
            for days_ago, price_xdays_ago in self.past_prices_close.items():
                if price_xdays_ago != 'NaN':
                    growth = ((price_latest - price_xdays_ago) * 100 / price_xdays_ago)
                    price_growth[days_ago] = growth
            price_growth.pop('Current', None)
        return price_growth

    # This function gets all the key ratios and creates a pickle for each category of key ratios, where they get saved.
    def save_keyratios(self):
        try:
            rev_growth_vals, inc_growth_vals, efficiency_vals, financials_vals, profitability_vals, cashflow_vals, liquidity_vals = self.get_all_keyratios()
        except ValueError:
            return print(f"Key Ratios for {self.ticker} could not be obtained.")
        # create a pickle for each category of key ratios.
        # Revenue growth ratios:
        stock_id = [self.name, self.isin, self.sector, self.stock_currency]
        # categories = {"rev_growth_data": rev_growth_vals, "inc_growth_data": inc_growth_vals}
        categories = {"rev_growth_data": rev_growth_vals, "inc_growth_data": inc_growth_vals, "efficiency_data": efficiency_vals, "financials_data": financials_vals, "profitability_data": profitability_vals, "cashflow_data": cashflow_vals, "liquidity_data": liquidity_vals}

        for pickle_name, category_vals in categories.items():
                # check if the value exists
            for ratio in category_vals:
                if ratio[-1] != "*":  # if the TTM data does not exist, we use the most recent year.
                    ratio_value = ratio[-1]
                elif ratio[-2] != "*":
                    ratio_value = ratio[-2]
                else:  # if the most recent year doesn't exist for this company then we don't count it in.
                    ratio_value = None
                if ratio_value is not None:
                    data = {
                        self.ticker: [ratio_value, stock_id]
                    }
                    data_dict = {ratio.name: data}
                    # save to the data pickle. If the pickle does not exist yet then create it.
                    if not os.path.isfile(f"data/pickles/{pickle_name}.pickle"):  # if the file doesn't exist then let's create it.
                        with open(f"data/pickles/{pickle_name}.pickle", "wb") as f:
                            pickle.dump(data_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
                    else:  # if the pickle already exists, let's open it and store the data with it.
                        old_data = pickle.load(open(f"data/pickles/{pickle_name}.pickle", "rb"))
                        if ratio.name in old_data:  # if the key ratio already exists in the dict then update it. Else add the key ratio.
                            old_data[ratio.name].update(data)
                        else:
                            old_data.update(data_dict)
                        with open(f'data/pickles/{pickle_name}.pickle', 'wb') as f:
                            pickle.dump(old_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                else:  # the ratio for the most recent period does not exists, so let's check if the old data is in the pickle.
                    if os.path.isfile(f"data/pickles/{pickle_name}.pickle"):  # if the pickle exists
                        old_data = pickle.load(open(f"data/pickles/{pickle_name}.pickle", "rb"))
                        if ratio.name in old_data:
                            if self.ticker in old_data[ratio.name]:  # if the ratio for the specific company exists we delete the outdated data.
                                del old_data[ratio.name][self.ticker]
                                with open(f'data/pickles/{pickle_name}.pickle', 'wb') as f:
                                    pickle.dump(old_data, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    start = time.time()
    end = time.time()
    print('time: ', end - start)
