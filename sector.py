import pandas as pd
import pickle
import statistics as st

class prepare_data(object):
    def __init__(self, ticker, isin, name, sector, icb):
        self.ticker = ticker
        self.isin = isin
        self.name = name
        self.sector = sector
        self.icb = icb
        # self.today = dt.date.today()
        # self.price_days_ago = [7, 14, 30, 60, 90, 180, 365, 730, 1095, 1825]  # 1w, 2w, 1m, 2m, 3m, 6m, 1y, 2y, 3y, 5y

    def get_eps(self):
        df_is = pd.read_csv(f'data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs', delimiter=',', header=1, skip_blank_lines=True, index_col=[0])
        df_is.drop(["Operating expenses", "Earnings per share", "Weighted average shares outstanding"], inplace=True)

        duplicates = df_is.index.duplicated(keep='last')
        num = 0
        dups_id = []
        for x in duplicates:
            if x:
                dups_id.append(num)
            num += 1
        try:
            eps_basic = df_is.iloc[dups_id[0]]
            eps_basic = eps_basic.to_dict()

            eps_diluted = df_is.iloc[dups_id[1]]
            eps_diluted = eps_diluted.to_dict()

        except IndexError:
            eps_basic = 'NaN'
            eps_diluted = 'NaN'

        return eps_basic, eps_diluted

class full_analysis(object):
    def __init__(self):
        self.universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))

    def sort_eps(self):
        # Earnings Per Share (EPS)
        eps_basic_nasdaqco = {}
        eps_diluted_nasdaqco = {}

        eps_basic_sector = {}
        eps_diluted_sector = {}

        for key_ticker, value in self.universe.items():
            # Eps
            stock = prepare_data(key_ticker, value[0], value[1], value[3], value[4])  # ticker, isin, name, sector, icb

            eps_basic, eps_diluted = stock.get_eps()

            if eps_basic and eps_diluted == 'NaN':
                print("error", key_ticker)
                pass
            else:
                eps_basic_nasdaqco[key_ticker] = eps_basic
                eps_diluted_nasdaqco[key_ticker] = eps_diluted

                if eps_basic_sector.get(value[3]) is None:
                    d = {}
                    d[key_ticker] = eps_basic
                    eps_basic_sector[value[3]] = d

                else:
                    d = {}
                    d[key_ticker] = eps_basic
                    eps_basic_sector[value[3]] = [eps_basic_sector[value[3]], d]

                if eps_diluted_sector.get(value[3]) is None:
                    d = {}
                    d[key_ticker] = eps_diluted
                    eps_diluted_sector[value[3]] = d
                else:
                    d = {}
                    d[key_ticker] = eps_diluted
                    eps_diluted_sector[value[3]] = [eps_diluted_sector[value[3]], d]

        print(eps_basic_nasdaqco)
        with open('data/Nasdaq_CO_Data/eps_basic_nasdaqco.pickle', 'wb') as f:
            pickle.dump(eps_basic_nasdaqco, f, protocol=pickle.HIGHEST_PROTOCOL)

        with open('data/Nasdaq_CO_Data/eps_diluted_nasdaqco.pickle', 'wb') as f:
            pickle.dump(eps_diluted_nasdaqco, f, protocol=pickle.HIGHEST_PROTOCOL)

        with open('data/SectorData/eps_basic_sector.pickle', 'wb') as f:
            pickle.dump(eps_basic_sector, f, protocol=pickle.HIGHEST_PROTOCOL)

        with open('data/SectorData/eps_diluted_sector.pickle', 'wb') as f:
            pickle.dump(eps_diluted_sector, f, protocol=pickle.HIGHEST_PROTOCOL)

    def eps_basic_nasdaq_avg(self):
        eps_basic_nasdaqco = pickle.load(open('data/Nasdaq_CO_Data/eps_basic_nasdaqco.pickle', 'rb'))

        eps_ttm = []
        eps_sum = 0

        for key_ticker, value in eps_basic_nasdaqco.items():
            ttm_value = value['TTM']
            eps_sum += ttm_value
            eps_ttm.append(ttm_value)

            print(key_ticker)
            print(value)

        eps_avg = {'length': len(eps_ttm), 'median': st.median(eps_ttm), 'arithmetic_avg': eps_sum / len(eps_ttm)}
        return eps_avg


if __name__ == '__main__':
    x = full_analysis()
    x.eps_basic_nasdaq_avg()
