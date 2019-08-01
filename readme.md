Architecture:

*app.py - runs the app and gets the layout for the specific url

    *server.py - runs the flask server and adds the external CSS and JS files.

    if index url
        get index page layout

    if company/{ticker}
        get layout for the specific company by companyLayout() from apps/company.py
            *company.py - creates the different components and stock price graph for the layout. A lot of the html comes from functions from components.py
                *components.py - creates the html for the components.

    *dataDownloads.py - downloads all of the necessary data files:
        save_nasdaqcph_companies():
            - All nasdaq cph companies are saved as a pickle file: data/pickles/universe_companies.pickle
                Dictionary, data structure: key[ticker] = values(isin, name, currency, sector, icb, omxc25)
            - All sectors in the market are saved as a pickle file: data/pickles/AllSectors.pickle
                (List)
            - Search data for all companies with their name and ticker saved as a pickle file: data/pickles/search.pickle
                (list)

        CompanyFinancialData(object):
            - Key ratios are saved as a cvs: data/CompanyData/{self.ticker}/{self.ticker}_KeyRatios.cvs
            - Balance sheet is saved as a cvs: data/CompanyData/{self.ticker}/{self.ticker}_BalanceSheet.cvs
            - Income statement is saved as a cvs: data/CompanyData/{self.ticker}/{self.ticker}_Income.cvs
            - Cash flow is saved as a cvs: data/CompanyData/{self.ticker}/{self.ticker}_CashFlow.cvs

        download_prices(ticker):
            - data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs

    *usedata.py - reads the data files (csv) so the data is usable.

    *settings.py

    *sector.py

    *stocks.py - unrelated to main app
