# import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import millify
import numpy as np
# import pp
import pickle
from settings import GRAPHSETTINGS as gs

def make_graph(value, color, graphtype):
    if graphtype == 'scatter2y':
        graph = go.Scatter(
            x=value.index.tolist(),
            y=value.get_values(),
            opacity=0.8,
            hoverinfo=gs['hoverinfo'],
            line=dict(color=color),
            mode='line',
            yaxis='y2'
        )
    elif graphtype == 'bar':
        graph = go.Bar(
            x=value.index.tolist(),
            y=value.get_values(),
            hoverinfo=gs['hoverinfo'],
            marker=go.Marker(
                color=(color),
                line=dict(
                    color='rgb(0, 0, 0)',
                    width=1.0
                )
            )
        )
    return graph

# make table from list of values. Index is a number that will be used as getting the index from the list. columns is the number of columns.

class Table(object):
    def __init__(self, values, index=0, title='', columns=4, html_class='', startrow=-1):
        self.values = values  # list of values.
        self.index = index  # what value should be used as the index for getting the culumns headers.
        self.title = title  # first culumn header.
        self.columns = columns  # amount of culumns to make.
        self.html_class = html_class  # add css classes.
        self.startrow = startrow  # what row to start at. Default gets -1 eg. the newest.

    # get rows.
    def get_tr(self, value, column_name, color_class, num):
        # first make a row with the title of the value.
        if column_name is None:
            title = str(value.name.title())
            if "Dkk" in title:
                title = title.replace("Dkk", "DKK")
            if "Eur" in title:
                title = title.replace("Eur", "EUR")
            if "Usd" in title:
                title = title.replace("Usd", "USD")
            if "*" in title:
                title = title.replace(" *", "")
            title = "  " + title
            rows = [html.Th([html.I("lens", className=f"tiny material-icons {color_class[num]}"), title], scope='row', className='table-th')]
        else:
            title = "  " + str(column_name[self.title_num])
            rows = [html.Th([html.I("lens", className=f"tiny material-icons {color_class[num]}"), title], scope="row", className="table-th")]
        # what values to get. Default is -1, so it gets the latest value.
        num = self.startrow
        # makes row for every column.
        for i in range(self.columns):
            # get the rows value.
            val = str(value.get_values()[num])
            if val == "*":
                val = "-"
            else:
                val = millify.prettify(val)
            rows.append(html.Td(val))
            num -= 1
        tr = html.Tr(rows)
        self.title_num += 1
        return tr

    # get headers for columns.
    def get_th(self):
        # first column header is title (default is nothing).
        th = [html.Th(self.title)]
        # what values to get. Default is -1, so it gets the latest value.
        num = self.startrow
        # make columns
        for i in range(self.columns):
            # takes the chosen index value and gets it's index values. Default takes the first value in the list and gets the newest value.
            th.append(html.Th(self.values[self.index].index.tolist()[num], scope="col"))
            num -= 1
        return th

    def make_graph_table(self, color_class, column_name=None, href=""):
        self.title_num = 0
        body = []
        num = 0
        for val in self.values:
            body.append(self.get_tr(val, column_name, color_class, num))
            num += 1
        table = html.Div(className=self.html_class, children=[
            html.Table(className='highlight centered', children=[
                html.Thead(html.Tr(
                    self.get_th(),
                )),
                html.Tbody(body)  # make row for all values.
            ]),
            html.Br(),
            html.A("See more", className="my-blue waves-effect waves-light btn right white-text", href=href)
        ])
        return table

    # add sector and market in later update.
    # tables for finance tabs tables
    def make_keyratios_table(self, company_name):
        html_content = []
        num = 0
        n = self.startrow
        market_avg = pickle.load(open("data/pickles/average_keyratios.pickle", "rb"))
        for val in self.values:  # val returns a list of pandas series that all use the same header columns.
            table = []

            tr = html.Thead([html.Tr([  # horizontal header showing the dates
                html.Th(),
                html.Th([self.values[num][self.index].index.tolist()[n[num]]], scope="col"),
                html.Th([self.values[num][self.index].index.tolist()[n[num] - 1]], scope="col"),
                html.Th([self.values[num][self.index].index.tolist()[n[num] - 2]], scope="col"),
                html.Th([self.values[num][self.index].index.tolist()[n[num] - 3]], scope="col"),
                html.Th([self.values[num][self.index].index.tolist()[n[num] - 4]], scope="col"),
                html.Th([self.values[num][self.index].index.tolist()[n[num] - 5]], scope="col"),
                html.Th("Market Average", scope='col')
            ])])
            table.append(tr)
            category = self.title[num]
            if category == "FINANCIALS":
                category = "financials_data"
            elif category == "PROFITABILITY":
                category = "profitability_data"
            elif category == "CASH FLOW":
                category = "cashflow_data"
            elif category == "LIQUIDITY":
                category = "liquidity_data"
            elif category == "EFFICIENCY":
                category = "efficiency_data"
            elif category == "REVENUE GROWTH":
                category = "rev_growth_data"
            elif category == "NET INCOME GROWTH":
                category = "inc_growth_data"
            for v in val:  # the rows
                market_avg_value = market_avg[category][v.name][0]
                market_avg_value = round(market_avg_value, 2)
                title = str(v.name.title())

                if "Dkk" in title:
                    title = title.replace("Dkk", "DKK")
                if "Eur" in title:
                    title = title.replace("Eur", "EUR")
                if "Usd" in title:
                    title = title.replace("Usd", "USD")
                if "Sek" in title:
                    title = title.replace("Sek", "SEK")
                if "Gbp" in title:
                    title = title.replace("Gbp", "GBP")
                if "*" in title:
                    title = title.replace(" *", "")
                if "Year Over Year" == title:
                    title = title + " %"
                if "3-Year Average" == title:
                    title = title + " %"
                if "5-Year Average" == title:
                    title = title + " %"
                if "10-Year Average" == title:
                    title = title + " %"

                rows_value = [html.Th([title], scope="row", className="table-th")]

                listed_values = [
                    str(v.get_values()[n[num]]),
                    str(v.get_values()[n[num] - 1]),
                    str(v.get_values()[n[num] - 2]),
                    str(v.get_values()[n[num] - 3]),
                    str(v.get_values()[n[num] - 4]),
                    str(v.get_values()[n[num] - 5]),
                    str(market_avg_value)
                ]
                for sort in listed_values:
                    if sort == "*":
                        value_sorted = "-"
                    else:
                        value_sorted = millify.prettify(sort)
                    rows_value.append(html.Td(value_sorted))

                row = html.Tbody([html.Tr(rows_value)])
                table.append(row)
            tables = html.Div([
                html.H5(self.title[num], className="center-align"),
                html.Div(className="divider"),
                html.Div([  # table
                    html.Table(table, className='highlight centered')
                ])
            ], className="col s12 pt15")
            html_content.append(tables)
            num += 1

        return html_content

# creating key stats table for company page
def table_keystats(stock):
    # Getting the data
    eps, payout_ratio, book_value_per_share, free_cash_flow, free_cash_flow_per_share = stock.get_financials()  # getting EPS, Payout ratio, Book value per share, Free cash flow, Free cash flow per share
    del free_cash_flow  # we don't want to include this one.
    pe = stock.calc_pe_ratio(eps)  # get P/E ratio
    shares = stock.get_number_of_shares()  # getting amount of shares
    returns = stock.stock_growth()
    if returns == "*":
        return_1yr = "-"
    elif "1y" in returns:
        return_1yr = returns["1y"]  # 1 yeah stock price return
        return_1yr = f"{round(return_1yr, 2)}%"
    else:
        return_1yr = "-"
    if stock.past_prices_close == "*":
        price_latest = "-"
    else:
        price_latest = stock.past_prices_close['Current']  # latest close price
        price_latest = round(float(price_latest), 3)

    volume_avg_30day = stock.calc_avg_volume(30)  # 30 day average stock trading volume

    if "," in str(shares['TTM']):
        shares_ttm = shares['TTM'].replace(",", "")
    else:
        shares_ttm = shares['TTM']

    if "," in str(shares[-2]):
        shares_2 = shares[-2].replace(",", "")
    else:
        shares_2 = shares[-2]

    if type(shares_ttm) is str and shares_ttm != "*":
        shares_ttm = float(shares_ttm)
    else:
        shares_ttm = shares_ttm

    if shares_ttm == 0 or np.isnan(shares_ttm):
        if shares_2 == 0 or np.isnan(shares_2):
            marketcap = "-"
            shares = "-"
        else:
            marketcap = price_latest * float(shares_2) * 1000000
            marketcap = f"{millify.millify(marketcap, precision=2)} {stock.stock_currency}"
            shares = shares_2 * 1000000
            shares = millify.millify(shares, precision=2)
    elif price_latest == "-":
        marketcap = "-"
    else:
        marketcap = price_latest * float(shares_ttm) * 1000000  # calculating market cap
        marketcap = f"{millify.millify(marketcap, precision=2)} {stock.stock_currency}"
        shares = shares_ttm * 1000000
        shares = millify.millify(shares, precision=2)

    if ".0" in str(price_latest):
        price_latest = str(price_latest).replace(".0", "")

    volume_avg_30day = millify.prettify(round(volume_avg_30day, 0)).replace(".0", "")

    def get_pdseries_html_row(pd_series):
        if type(pd_series["TTM"]) is str and pd_series['TTM'] != "*":
            pd_series_ttm = float(pd_series["TTM"])
        else:
            pd_series_ttm = pd_series["TTM"]
        if pd_series_ttm == "*" or np.isnan(pd_series_ttm):  # no data for ttm
            # bad data check
            if type(pd_series[-2]) is str and pd_series[-2] != "*":
                pd_series_2 = float(pd_series[-2])
            else:
                pd_series_2 = pd_series[-2]
            if pd_series_2 == "*" or np.isnan(pd_series_2):  # no data in latest period either. We can't use this data.
                value = "-"  # null value
                name = pd_series.name
            else:  # use from newest annual period
                value = pd_series_2
                name = pd_series.name + " (" + pd_series.index[-2] + ")"
        else:  # use from TTM
            value = pd_series_ttm
            name = pd_series.name + " (TTM)"

        if " *" in name:
            name = name.replace(" *", "")
        if value != "-":
            value = millify.millify(value, precision=2)

        if " %" in name:
            name = name.replace(" %", "")
            if value != "-":
                value = str(value) + "%"
        if " EUR" in name:
            name = name.replace(" EUR", "")
            if value != "-":
                value = str(value + " EUR")
        if " DKK" in name:
            name = name.replace(" DKK", "")
            if value != "-":
                value = str(value + " DKK")
        if " USD" in name:
            name = name.replace(" USD", "")
            if value != "-":
                value = str(value + " USD")
        html_row = [html.Td([name]), html.Td([value], className="right-align bold")]

        return html_row

    if type(pe) is str:
        pe = "-"
    else:
        pe = round(pe, 2)
    # creating html for table
    table = html.Table([
        html.Tbody([
            html.Tr([  # P/E row
                html.Td(["P/E Ratio"]),
                html.Td([pe], className="right-align bold")
            ]),
            html.Tr([  # Latest price row
                html.Td(["Latest Price"]),
                html.Td([f"{price_latest} {stock.stock_currency}"], className="right-align bold")
            ]),
            html.Tr([  # Average 30-day volume row
                html.Td(["30 Day Avg Volume"]),
                html.Td([volume_avg_30day], className="right-align bold")
            ]),
            html.Tr([  # Market cap row
                html.Td(["Market Cap"]),
                html.Td([marketcap], className="right-align bold")
            ]),
            html.Tr([  # Number of Shares row
                html.Td(["Number of Shares"]),
                html.Td([shares], className="right-align bold")
            ]),
            html.Tr([  # 1 year return row
                html.Td(["1 Year Return"]),
                html.Td([return_1yr], className="right-align bold")
            ]),
            html.Tr(get_pdseries_html_row(eps)),
            html.Tr(get_pdseries_html_row(book_value_per_share)),
            html.Tr(get_pdseries_html_row(free_cash_flow_per_share)),
            html.Tr(get_pdseries_html_row(payout_ratio)),
            html.Tr([  # Sector row
                html.Td(["Sector"]),
                html.Td([stock.sector], className="right-align bold")
            ])
        ])
    ], className="highlight")
    return table
