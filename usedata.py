import pandas as pd
# import pickle
import datetime as dt
# import dataDownloads
import time

class Stock(object):
    def __init__(self, ticker, name, isin, sector, stock_currency):
        self.ticker = ticker.upper()
        self.name = name
        self.isin = isin
        self.sector = sector
        self.stock_currency = stock_currency
        self.today = dt.date.today()
        self.past_prices_close = self.historical_stock_price_close()

    # From key ratios get Revenue, Gross Margin, Operating Income, Operating Margin and Net Income.
    def get_income(self):
        df_revenue = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=0, skip_blank_lines=True, index_col=[0], skiprows=range(0, 2), nrows=5)
        df_revenue.fillna('*', inplace=True)
        revenue = df_revenue.iloc[0]
        grossMargin = df_revenue.iloc[1]
        operatingIncome = df_revenue.iloc[2]
        operatingMargin = df_revenue.iloc[3]
        netIncome = df_revenue.iloc[4]
        return revenue, grossMargin, operatingIncome, operatingMargin, netIncome  # returns as a pandas Series.

    # Open the balance sheet
    def open_balance(self):
        df_balance = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0], error_bad_lines=False)
        df_balance.fillna('*', inplace=True)
        return df_balance

    # From balance sheet get total assets and liabilities.
    def get_balance(self):
        df_balance = self.open_balance()
        print("open_balance function success")
        assets = df_balance.loc['Total assets']
        liabilities = df_balance.loc['Total liabilities']
        print(assets, liabilities)
        return assets, liabilities  # returns as a pandas Series.

    # Open the cash flow statement
    def open_cashflow(self):
        df_cashflow = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0])
        df_cashflow.fillna('*', inplace=True)
        return df_cashflow

    # From cash flow statement get operating, investing and financing activities.
    def get_cashflow(self):
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
        return operating, investing, financing  # returns as a pandas Series.

    def get_financials(self):
        df_financials = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=15)
        df_financials.fillna('*', inplace=True)
        eps = df_financials.iloc[5]
        print(eps)
        payout_ratio = df_financials.iloc[7]
        book_value_per_share = df_financials.iloc[9]
        free_cash_flow = df_financials.iloc[12]
        free_cash_flow_per_share = df_financials.iloc[13]
        return eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share

    # Calculates P/E ratio: Current price / EPS(ttm)
    def get_pe_ratio(self, eps):
        # if eps does not exist for that year
        pe = self.past_prices_close['Current'] / float(eps[-1])
        print(float(eps[-1]))
        print(pe)
        return pe

    def get_debt_ratio(self):
        df_balance = self.open_balance()
        liabilities = df_balance.loc['Total liabilities']
        assets = df_balance.loc['Total assets']
        debt_ratio = liabilities / assets
        return debt_ratio

    # Enterprise value: market cap + total borrowing - cash
    def get_enterprise_value(self):
        df_keyratios = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=10)
        shares = df_keyratios.iloc[8]['TTM']
        marketcap = self.past_prices_close['Current'] * float(shares)
        df_balance = self.open_balance()
        long_term_debt = df_balance.loc['Long-term debt'][-1]
        try:
            short_term_debt = float(df_balance.loc['Short-term debt'][-1])
        except ValueError:  # fix error if data is empty
            short_term_debt = 0.0
        cash = df_balance.loc['Cash and cash equivalents'][-1]
        enterprise_value = marketcap + short_term_debt + long_term_debt - cash
        return enterprise_value

    # calculate cash flow ratio: cash flow from operations / current liabilities
    def get_cash_flow_ratio(self):
        df_balance = self.open_balance()
        liabilities = df_balance.loc['Total current liabilities']

        df_cashflow = self.open_cashflow()
        try:
            operating_cf = df_cashflow.loc['Net cash provided by operating activities']
        except KeyError:
            try:
                operating_cf = df_cashflow.loc['Operating cash flow']
            except KeyError:
                operating_cf = None

        if operating_cf is None:
            cash_flow_ratio = '*'
        else:
            cash_flow_ratio = operating_cf / liabilities
        print(cash_flow_ratio)
        return cash_flow_ratio

    # From key ratios get growth in revenue and net income.
    def get_all_keyratios(self):
        df_kr = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs', delimiter=',', header=0, skip_blank_lines=True, index_col=[0], skiprows=range(0, 20))
        df_kr.fillna('*', inplace=True)
        # growth
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
        # Cashflow ratios
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
        # Cashflow ratios
        except KeyError:  # some companies dont have free cashflow to income.
            cashflow_vals_unsorted = [cap_ex_sales, freecashflow_to_sales]  # combining them to a list
            for val in cashflow_vals_unsorted:  # Do not add value if only NaN values.
                if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
                    pass
                else:
                    cashflow_vals.append(val)  # append those that are not only nan values.
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
        # P/E ratio
        eps = self.get_pe_ratio(eps)
        print("get_pe_ratio function success")
        return rev_growth_vals, inc_growth_vals, efficiency_vals, financials_vals, profitability_vals, cashflow_vals, liquidity_vals

    # Function getting a date x days ago.
    def time_ago(self, time):
        time_ago = self.today - dt.timedelta(days=time)
        return time_ago

    def historical_stock_price_close(self):
        df_price = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_AdjDailyPrices.cvs', delimiter=',', header=0, skip_blank_lines=True)
        df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])
        df_price.set_index('timestamp', inplace=True)
        past_prices_close = {}  # saving prices in a dict
        # Getting the latest price
        price_latest = (df_price['close'][0])
        if price_latest == 0:
            attempt = 1
            while price_latest == 0 and attempt < 10:  # if market is closed this day go to latest open day.
                price_latest = (df_price['adjusted_close'][attempt])
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
        # print(past_prices_close)
        return past_prices_close

    def stock_growth(self):
        # Stock growth since x days ago
        price_latest = self.past_prices_close['Current']
        price_growth = {}
        for days_ago, price_xdays_ago in self.past_prices_close.items():
            if price_xdays_ago != 'NaN':
                growth = ((price_latest - price_xdays_ago) * 100 / price_xdays_ago)
                price_growth[days_ago] = growth
        price_growth.pop('Current', None)
        print(price_growth)
        return price_growth


if __name__ == '__main__':
    start = time.time()

    x = Stock('tcm.co', "", "", "", "")
    x.get_all_keyratios()
    # x.get_enterprise_value()

    end = time.time()
    print('time: ', end - start)
