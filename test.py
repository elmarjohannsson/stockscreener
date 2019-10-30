import pandas as pd
import copy
import os
from settings import PATH
import pickle
import datetime as dt
# Returns financial values by opening the company's key ratios sheet and searching for wanted values
ticker = "SAS-DKK.CPH"
df_financials = pd.read_csv(f'data/CompanyData/{ticker}/{ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=15)
df_financials.fillna('*', inplace=True)
eps = df_financials.iloc[5]
payout_ratio = df_financials.iloc[7]
book_value_per_share = df_financials.iloc[9]
free_cash_flow = df_financials.iloc[12]
free_cash_flow_per_share = df_financials.iloc[13]

eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share

financials_vals_unsorted = [eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share]
financials_vals = []
for val in financials_vals_unsorted:  # Do not add value if only NaN values.
    if val[-1] == val[-2] == val[-3] == val[-4] == val[-5] == val[-6] == '*':
        pass
    else:
        financials_vals.append(val)  # append those that are not only nan values.

# # changing the financials values, so it is the same currency for all.

universal_vals = copy.deepcopy(financials_vals)
n = 0
delete = []


for ratio in universal_vals:
    if "DKK" in ratio.name:
        # put into universal ratio
        ratio.name = ratio.name + " Universal"
    elif "EUR" in ratio.name:
        # changes the currency to DKK and puts it into the Universal one.
        from_currency = "EUR"
        ratio.name = ratio.name.replace("EUR", "DKK") + " Universal"

    elif "USD" in ratio.name:
        from_currency = "USD"
        ratio.name = ratio.name.replace("USD", "DKK") + " Universal"
    elif "GBP" in ratio.name:
        from_currency = "GBP"
        ratio.name = ratio.name.replace("GBP", "DKK") + " Universal"
    elif "SEK" in ratio.name:
        from_currency = "SEK"
        ratio.name = ratio.name.replace("SEK", "DKK") + " Universal"
        print(ratio[-1], "SEK")
    else:
        delete.append(n)

    to_currency = "DKK"

    if os.path.isfile(f"{PATH}/data/pickles/currencies.pickle"):  # check data for currency rate.
        currencies = pickle.load(open(f'{PATH}/data/pickles/currencies.pickle', 'rb'))
        if f"{from_currency}to{to_currency}" in currencies:  # check if we have for what we need now.
            days_since_update = self.today - currencies[f"{from_currency}to{to_currency}"]["updated"]
            if days_since_update > dt.timedelta(5):  # check if the data is too old (5 day) to be used reliably
                fx = self.update_currency(currencies, to_currency)
            else:
                fx = currencies[f"{from_currency}to{to_currency}"]["Rate"]
        else:
            fx = self.update_currency(currencies, to_currency)
    else:  # if the file doesn't exist then let's create it.
        currencies = {}
        fx = self.update_currency(currencies, to_currency)

    ratio[-1] = ratio[-1] * fx
    ratio[-2] = ratio[-2] * fx

    n += 1

if delete:  # if list is not empty
    for number in delete:
        print(number, "delete")
        del universal_vals[number]

# financials_vals.extend(universal_vals)
print(universal_vals, "universal")
# print(financials_vals, "NORMAL")
# print(financials_vals, type(financials_vals))
