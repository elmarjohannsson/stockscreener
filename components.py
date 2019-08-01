# import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import millify
import numpy as np

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
    def get_tr(self, value, column_name):
        # first make a row with the title of the value.
        if column_name is None:
            td = [html.Td(value.name.title())]
        else:
            td = [html.Td(column_name[self.title_num])]
        # what values to get. Default is -1, so it gets the latest value.
        num = self.startrow
        # makes row for every column.
        for i in range(self.columns):
            # get the rows value.
            td.append(html.Td(str(value.get_values()[num]).upper()))
            num -= 1
        tr = html.Tr(td)
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
            th.append(html.Th(self.values[self.index].index.tolist()[num]))
            num -= 1
        return th

    def make_graph_table(self, column_name=None):
        self.title_num = 0
        table = html.Div(className=self.html_class, children=[
            html.Table(className='', children=[
                html.Thead(html.Tr(
                    self.get_th(),
                )),
                html.Tbody(
                    # make row for all values.
                    [self.get_tr(val, column_name) for val in self.values]
                )
            ])
        ])
        return table

    # With sector and market for later update.
    def make_keyratios_table(self, company_name):
        table_content = [html.Tr([
            html.Th(f'Key Ratios for {company_name}', colSpan='6')
        ])
        ]
        # Row 2 - secondary columns, headers for values
        num = 0
        n = self.startrow
        for val in self.values:  # val returns a list of pandas series that all use the same header columns.
            # print('Index list', self.values[num][self.index].index.tolist())
            # print('current num', num)
            table_index = html.Tr([
                # first is index column
                html.Td(self.title[num]),
                # next four are for the stock
                html.Td(self.values[num][self.index].index.tolist()[n[num]]),
                html.Td(self.values[num][self.index].index.tolist()[n[num] - 1]),
                html.Td(self.values[num][self.index].index.tolist()[n[num] - 2]),
                html.Td(self.values[num][self.index].index.tolist()[n[num] - 3]),
                html.Td(self.values[num][self.index].index.tolist()[n[num] - 4]),
                html.Td(self.values[num][self.index].index.tolist()[n[num] - 5])
            ], className='')
            table_content.append(html.Br()),
            table_content.append(table_index)
            for v in val:
                # print('the value2', v)
                table_values = html.Tr([
                    # first is index column
                    html.Td(v.name.title()),
                    # next four are for stock
                    html.Td(str(v.get_values()[n[num]]).upper()),
                    html.Td(str(v.get_values()[n[num] - 1]).upper()),
                    html.Td(str(v.get_values()[n[num] - 2]).upper()),
                    html.Td(str(v.get_values()[n[num] - 3]).upper()),
                    html.Td(str(v.get_values()[n[num] - 4]).upper()),
                    html.Td(str(v.get_values()[n[num] - 5]).upper())
                ])
                table_content.append(table_values)
            num += 1

        table = html.Table(className='', children=table_content)
        return table

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
        print(returns, type(returns), "SDASDSADSA")
        return_1yr = returns["1y"]  # 1 yeah stock price return
        return_1yr = f"{round(return_1yr, 2)}%"
    else:
        return_1yr = "-"

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
        ])
    ], className="highlight")
    return table
