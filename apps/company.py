# This file creates the layout for each individual firms page on the url /company/ticker
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime as dt
import plotly.graph_objs as go
from server import app
import pandas as pd
import os

import usedata
import components
from settings import GRAPHSETTINGS as gs

# making the html component for the graphs of the companies financials.
def get_financial_graphs(stock):
    # Getting the keyratios for the financials graphs and checking if the files are empty. If they are they should not be added.
    kr_url = f'data/CompanyData/{stock.ticker}/{stock.ticker}_KeyRatios.cvs'
    # if keyratios.cvs is not empty then get it
    if not os.path.isfile(kr_url):
        add_income = False
    elif os.stat(kr_url).st_size == 0:
        add_income = False
    else:
        revenue, grossMargin, operatingIncome, operatingMargin, netIncome = stock.get_income()
        add_income = True

    bs_url = f'data/CompanyData/{stock.ticker}/{stock.ticker}_BalanceSheet.cvs'
    # if balance sheet is not empty then get it
    if not os.path.isfile(bs_url):
        add_balance = False
    elif os.stat(bs_url).st_size == 0:
        add_balance = False
    else:
        assets, liabilities = stock.get_balance()
        add_balance = True

    cf_url = f'data/CompanyData/{stock.ticker}/{stock.ticker}_CashFlow.cvs'
    # if cash flow is not empty then get it
    if not os.path.isfile(cf_url):
        add_cashflow = False
    elif os.stat(cf_url).st_size == 0:
        add_cashflow = False
    else:
        operating, investing, financing = stock.get_cashflow()
        add_cashflow = True

    financial_graphs = []

    if add_income:
        # start and end range for income statement. Showing TTM and last three fiscal years.
        is_maxrange = len(revenue.index.tolist()) - 0.5
        is_startrange = is_maxrange - 4
        # Income Statement Graph
        income_statement = html.Div(className='', children=[
            dcc.Graph(
                id='is_graph',
                config=gs['config'],
                figure=go.Figure(
                    data=[
                        components.make_graph(revenue, '#33cc33', 'bar'),
                        components.make_graph(operatingIncome, '#2C02F5', 'bar'),
                        components.make_graph(netIncome, '#7C02F5', 'bar'),
                        components.make_graph(grossMargin, '#00fbb8', 'scatter2y'),
                        components.make_graph(operatingMargin, '#36hbb1', 'scatter2y')
                    ],
                    layout=go.Layout(
                        title='Annual Income Statement',
                        dragmode=gs['dragmode'],
                        hovermode=gs['hovermode'],
                        showlegend=gs['showlegend'],
                        autosize=True,
                        xaxis=dict(
                            type='category',
                            range=[is_startrange, is_maxrange]),
                        yaxis2=dict(
                            overlaying='y',
                            side='right'),
                        margin=go.Margin(l=30, r=30, t=30, b=40)
                    )
                )
            )
        ])
        # make table for income statement. One row for each value in row.
        income_table = components.Table([revenue, operatingIncome, netIncome, grossMargin, operatingMargin], html_class='').make_graph_table()
        financial_graphs.append(income_statement)
        financial_graphs.append(income_table)
        print("Income added")
    if add_balance:
        # start and end range for balance sheet. Showing last four balance sheets
        bs_maxrange = len(assets.index.tolist()) - 0.5
        bs_startrange = bs_maxrange - 4
        # Balance Sheet Graph
        balance_sheet = html.Div(className='', children=[
            dcc.Graph(
                id='bs_graph',
                config=gs['config'],
                figure=go.Figure(
                    data=[
                        components.make_graph(assets, '#33cc33', 'bar'),
                        components.make_graph(liabilities, '#2C02F5', 'bar')
                    ],
                    layout=go.Layout(
                        title='Balance sheet',
                        dragmode=gs['dragmode'],
                        hovermode=gs['hovermode'],
                        showlegend=gs['showlegend'],
                        autosize=True,
                        xaxis=dict(
                            type='category',
                            range=[bs_startrange, bs_maxrange]),
                        yaxis2=dict(
                            overlaying='y',
                            side='right'),
                        margin=go.Margin(l=40, r=0, t=40, b=30)
                    )
                )
            ),
        ])
        # make table for balance sheet. One row for each value in row.
        balance_sheet_table = components.Table([assets, liabilities], html_class='').make_graph_table()
        financial_graphs.append(balance_sheet)
        financial_graphs.append(balance_sheet_table)
        print("Balance added")

    if add_cashflow:
        # start and end range for cash flow. Showing TTM and last three fiscal years.
        cf_maxrange = len(financing.index.tolist()) - 0.5
        cf_startrange = cf_maxrange - 4

        if operating is None:
            graph_data = [components.make_graph(investing, '#33cc33', 'bar'), components.make_graph(financing, '#2C02F5', 'bar')]
            cashflow_table = components.Table([investing, financing], html_class='').make_graph_table(['Investing Activities', 'Financing Activities'])
        else:
            graph_data = [components.make_graph(operating, '#53fc43', 'bar'), components.make_graph(investing, '#33cc33', 'bar'), components.make_graph(financing, '#2C02F5', 'bar')]
            cashflow_table = components.Table([operating, investing, financing], html_class='').make_graph_table(['Operating Activities', 'Investing Activities', 'Financing Activities'])
        # Cash Flow Graph
        cashflow = html.Div(className='', children=[
            dcc.Graph(
                id='cf_graph',
                config=gs['config'],
                figure=go.Figure(
                    data=graph_data,
                    layout=go.Layout(
                        title='Cash Flow',
                        dragmode=gs['dragmode'],
                        hovermode=gs['hovermode'],
                        showlegend=gs['showlegend'],
                        autosize=True,
                        xaxis=dict(
                            type='category',
                            range=[cf_startrange, cf_maxrange]),
                        yaxis=dict(fixedrange=gs['fixedrange']),
                        margin=go.Margin(l=40, r=0, t=40, b=30)
                    )
                )
            )
        ])
        financial_graphs.append(cashflow)
        financial_graphs.append(cashflow_table)

    financials_html = html.Div(className='', children=[
        html.Div(className='', children=financial_graphs)
    ])
    print("Cashflow added")
    return financials_html

# creating the table component for the stock price growth.
def get_stock_growth(stock):
    price_growth = stock.stock_growth()
    if price_growth == "*":
        table = html.Div(className='', children=[
            html.Div(className='', children=[
                html.Div(className='', children=html.H4('Sorry, prices are unavailable.'))
            ])
        ])
    else:
        td = []
        th = []
        for key, val in price_growth.items():
            if str(key) in "2w 2m 2y":
                continue
            if "1w" in str(key):
                key = str(key).replace("w", " Week")
            elif "w" in str(key):
                key = str(key).replace("w", " Weeks")

            if "1m" in str(key):
                key = str(key).replace("m", " Month")
            elif "m" in str(key):
                key = str(key).replace("m", " Months")

            if "1y" in str(key):
                key = str(key).replace("y", " Year")
            elif "y" in str(key):
                key = str(key).replace("y", " Years")

            td.append(html.Td("{0:.2f}%".format(val), className="center-align"))
            th.append(html.Th(key, className="center-align bold"))

        table = html.Table(className='col s11', children=[html.Thead(html.Tr(th)), html.Tbody(html.Tr(td))])
    return table

# creating the table component for all of the key ratios.
def get_keyratios_table(stock):
    if os.stat(f'data/CompanyData/{stock.ticker}/{stock.ticker}_KeyRatios.cvs').st_size == 0:
        keyratios_html = html.Div(className='', children=[
            html.H5(f'*Key Ratios do not exist for {stock.name}')
        ])
    else:
        rev_growth_vals, inc_growth_vals, efficiency_vals, financials_vals, profitability_vals, cashflow_vals, liquidity_vals = stock.get_all_keyratios()
        # print("get_all_keyratios function success")
        all_keyratios = [financials_vals, profitability_vals, cashflow_vals, liquidity_vals, efficiency_vals, rev_growth_vals, inc_growth_vals]
        keyratios_name = ["Financials", "Profitability", "Cash Flow", "Liquidity", "Efficiency", "Revenue growth, %", "Net income growth, %"]
        keyratios_startrow = [-1, -1, -1, -1, -1, -1, -2]
        num = 0
        for val in all_keyratios:
            if val == []:  # if list is empty then we don't want to add it.
                all_keyratios.remove(val)
                del(keyratios_name[num])
                del(keyratios_startrow[num])
            num += 1

        keyratios_html = html.Div(className='', children=[
            html.Div(className='', children=[
                html.Div(className='', children=[
                    components.Table(
                        all_keyratios,
                        title=[val for val in keyratios_name],
                        startrow=[val for val in keyratios_startrow]
                    ).make_keyratios_table(stock.name)
                ])
            ])
        ])
    return keyratios_html

def get_graph_key_stats_section(stock):
    section_one_html = html.Div([  # section div
        html.Div([  # row div
            html.Div([  # col 12 div
                html.H4(f'{stock.name}', className='center-align')
            ], className='col s12'),
            html.Div([
                html.Div(className="divider"),
                html.H5(f"STOCK PERFORMANCE ({stock.stock_currency})", className="center-align"),
                html.Div([  # col 10 for graph
                    dcc.Graph(id='stock_graph', config=gs['config'])
                ], className='col s11'),
                html.Div([  # col-2 for checklist menu
                    dcc.Checklist(  # checklist for graph settings
                        id='dropdown_graph_options',
                        className="",
                        options=[
                            {'label': 'Close', 'value': 3},
                            {'label': 'High', 'value': 1},
                            {'label': 'Low', 'value': 2},
                            {'label': 'Adjusted Close', 'value': 4}
                        ],
                        value=[3],
                        labelClassName="checkbox",
                        inputClassName="",
                        labelStyle={"display": "block"}
                    )
                ], className='col s1'),
                get_stock_growth(stock),  # Stock growth section
            ], className='col l9 push-l3 s12'),
            html.Div([  # key statistics table col 4
                html.Div(className="divider"),
                html.H5("KEY STATISTICS", className="center-align"),
                components.table_keystats(stock)
            ], className='col l3 pull-l9 s8 offset-s2')
            # insert key stat table here
        ], className='row'),
    ], className='section')
    return section_one_html

# the final layout that adds all of the components together.
def companyLayout(ticker, name, isin, sector, stock_currency):
    stock = usedata.Stock(ticker, name, isin, sector, stock_currency)
    # html layout
    layout = html.Div([
        dcc.Location(id='url2', refresh=False),
        get_graph_key_stats_section(stock),
        html.Br(),
        get_financial_graphs(stock),  # Financial graphs section
        # get_keyratios_table(stock),  # financial key ratios section
    ])
    return layout

# when there are any changes done to the stock price graph this call back function gets called and updates the graph.
# This is also were all of the settings and behavior of the graph is determined.
@app.callback(
    Output('stock_graph', 'figure'),
    [Input('dropdown_graph_options', 'value'),
     Input('stock_graph', 'relayoutData'),
     Input('url2', 'pathname')
     ]
)
def update_graph(value, relayoutData, pathname):
    graph = []
    if isinstance(pathname, str) and pathname.startswith('/company/'):
        # Ticker should be what comes after company/
        ticker = pathname[9:].upper()
    # Getting the data
    df = pd.read_csv(f'data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs')
    df = df.set_index('timestamp')
    df = df[(df.close != 0)]  # drop rows with an error.

    def append_graph(name, data, color):
        graph.append(go.Scatter(
            x=df.index,
            y=data,
            opacity=0.8,
            name=name,
            line=dict(color=color),
            mode="line",
        ))
    graphValues = {1: ['High', df.high, '00CBB4'], 2: ['Low', df.low, 'FF797E'], 3: ['Close', df.close, "2B2859"], 4: ['Adj. Close', df.adjusted_close, '665BB3']}
    for val in value:
        append_graph(graphValues[val][0], graphValues[val][1], graphValues[val][2])

    today = dt.date.today()
    yearago = today - dt.timedelta(days=181)
    startdict = {'autosize': True}
    autorange = {'xaxis.autorange': True}

    # print('RelayoutData: ', relayoutData)

    # Default. When the data is default set it to show data one year from today
    if relayoutData == startdict or relayoutData is None:
        startdate = yearago
        enddate = today
        # print(startdate, 'startdate1')
        # print(enddate, 'enddate1')

    # When 'all' button is pressed.
    elif relayoutData == autorange:
        startdate = df.index[-1]
        enddate = df.index[0]
        # print(startdate, 'startdate2')
        # print(enddate, 'enddate2')

    # When user is using the other buttons.
    # Relayout data is  either a Dict with 2 keys or 4.
    elif len(relayoutData) in [2, 4]:
        startdate = relayoutData['xaxis.range[0]']
        enddate = relayoutData['xaxis.range[1]']
        # print(startdate, 'startdate3')
        # print(enddate, 'enddate3')

    else:
        startdate = relayoutData['xaxis.range'][0]
        enddate = relayoutData['xaxis.range'][1]
        # print(startdate, 'startdate4')
        # print(enddate, 'enddate4')

    # End date has to be a dt.date obj.
    if isinstance(enddate, dt.date) is False:
        # if end date is a string then convert it to a date obj.
        if isinstance(enddate, str):
            enddate = dt.datetime.strptime(enddate[:10], '%Y-%m-%d').date()
            # print('enddate converted from string obj to date obj')
            # print('enddate result: ', enddate)

        # if end date is a datetime obj then convert it to a date obj.
        if isinstance(enddate, dt.datetime):
            enddate = enddate.date()
            # print('enddate converted from datetime obj to date obj')
            # print('enddate result: ', enddate)

    # Start date has to be a dt.date obj.
    if isinstance(startdate, dt.date) is False:
        # if start date is a string then convert it to a date obj.
        if isinstance(startdate, str):
            startdate = dt.datetime.strptime(startdate[:10], '%Y-%m-%d').date()
            # print('startdate converted from string obj to date obj')
            # print('startdate result: ', startdate)

        # if start date is a datetime obj then convert it to a date obj.
        elif isinstance(startdate, dt.datetime):
            startdate = startdate.date()
            # print('startdate converted from datetime obj to date obj')
            # print('startdate result: ', startdate)

    # startdate is after enddate then they get reversed.
    if startdate > enddate:
        newenddate = startdate
        newstartdate = enddate
        enddate = newenddate
        startdate = newstartdate

    # if end date is after todays date
    if enddate is not None and enddate > today:
        enddate = today

    # if start date is before the last date in the data make it equal to the last date.
    lastdataDate = dt.datetime.strptime(df.index[-1], '%Y-%m-%d').date()
    if startdate is not None and startdate < lastdataDate:
        startdate = lastdataDate

    # if end date is less than the last date in the data then set it to last date + 1 day.
    if enddate < lastdataDate:
        enddate = lastdataDate + dt.timedelta(days=7)

    # if start data is the same as end data then make startdata 1 day earlier.
    if startdate == enddate:
        startdate = enddate - dt.timedelta(days=1)

    # dynamic y-axis to the max and min value in the data in the current period.
    if 1 in value:  # if high is selected
        maxval = df.high.loc[str(enddate):str(startdate)].max()
    elif 3 in value:  # elif close is selected
        maxval = df.close.loc[str(enddate):str(startdate)].max()
    elif 2 in value and 4 in value:  # elif adj. close and low are selected use the highest.
        maxlow = df.low.loc[str(enddate):str(startdate)].max()
        maxadjclose = df.adjusted_close.loc[str(enddate):str(startdate)].max()
        if maxlow > maxadjclose:
            maxval = maxlow
        else:
            maxval = maxadjclose
    elif 4 in value:  # elif adj. close is selected
        maxval = df.adjusted_close.loc[str(enddate):str(startdate)].max()
    else:  # else only low is selected
        maxval = df.low.loc[str(enddate):str(startdate)].max()

    maxval = maxval * 1.01  # 1% upper margin

    if 2 in value and 4 in value:  # if low and adj close are selected
        minlow = df.low.loc[str(enddate):str(startdate)].min()
        minadjclose = df.adjusted_close.loc[str(enddate):str(startdate)].min()
        if minlow < minadjclose:  # use the one with lowest value
            minval = minlow
        else:
            minval = minadjclose
    elif 2 in value:  # elif low is selected
        minval = df.low.loc[str(enddate):str(startdate)].min()
    elif 4 in value:  # elif adj. close is selected
        minval = df.adjusted_close.loc[str(enddate):str(startdate)].min()
    elif 3 in value:  # elif close is selcted
        minval = df.close.loc[str(enddate):str(startdate)].min()
    else:  # else high is selected
        minval = df.high.loc[str(enddate):str(startdate)].min()

    minval = minval * 0.99  # 1% lower margin

    # rangeslider max and min values
    rangemax = df.high.max()
    rangemin = df.low.min()

    # print('finalend ', enddate, type(enddate))
    # print('finalstart ', startdate, type(startdate))
    # print("update_graph function success")
    return {
        'data': graph,
        'layout': go.Layout(
            # title="Chart",
            height=700,
            margin=go.Margin(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=0),
            yaxis=dict(
                range=[minval, maxval]
            ),
            xaxis=dict(
                range=[startdate, enddate],
                rangeselector=dict(
                    buttons=list([
                        dict(count=7,
                             label='1W',
                             step='day',
                             stepmode='backward'),
                        dict(count=1,
                             label='1M',
                             step='month',
                             stepmode='backward'),
                        dict(count=3,
                             label='3M',
                             step='month',
                             stepmode='backward'),
                        dict(count=6,
                             label='6M',
                             step='month',
                             stepmode='backward'),
                        dict(count=1,
                             label='YTD',
                             step='year',
                             stepmode='todate'),
                        dict(count=1,
                             label='1Y',
                             step='year',
                             stepmode='backward'),
                        dict(count=2,
                             label='2Y',
                             step='year',
                             stepmode='backward'),
                        dict(count=5,
                             label='5Y',
                             step='year',
                             stepmode='backward'),
                        dict(step='all', label="All")
                    ])
                ),
                rangeslider=dict(
                    yaxis=dict(
                        range=[rangemin, rangemax],
                        rangemode='fixed'
                    ),
                    range=[lastdataDate, today],
                    bgcolor="#6154B"
                ),
                type='date'
            ),
            showlegend=False,
            dragmode='pan'
        )
    }
