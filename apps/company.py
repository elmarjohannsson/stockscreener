# This file creates the layout for each individual firms page on the url /company/ticker
import bs4 as bs
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime as dt
import plotly.graph_objs as go
from server import app
import requests
import pandas as pd
import os
# import pp
import millify
import usedata
import components
from settings import PATH, GRAPHSETTINGS as gs

# making the html component for the graphs of the companies financials.
def get_financial_graphs(stock):
    # Getting the keyratios for the financials graphs and checking if the files are empty. If they are they should not be added.
    kr_url = f'{PATH}/data/CompanyData/{stock.ticker}/{stock.ticker}_KeyRatios.cvs'
    # if keyratios.cvs is not empty then get it
    if not os.path.isfile(kr_url):
        add_income = False
    elif os.stat(kr_url).st_size == 0:
        add_income = False
    else:
        revenue, grossMargin, operatingIncome, operatingMargin, netIncome = stock.get_income()
        add_income = True

    bs_url = f'{PATH}/data/CompanyData/{stock.ticker}/{stock.ticker}_BalanceSheet.cvs'
    # if balance sheet is not empty then get it
    if not os.path.isfile(bs_url):
        add_balance = False
    elif os.stat(bs_url).st_size == 0:
        add_balance = False
    else:
        assets, liabilities = stock.get_balance()
        debt_ratio = stock.calc_debt_ratio()
        if type(debt_ratio) is str:
            if debt_ratio == "*":
                add_balance = [True, False]
        else:
            debt_ratio = pd.Series(debt_ratio, name="Debt to Assets %")
            debt_ratio = debt_ratio.astype(float) * 100
            debt_ratio = debt_ratio.round(2)
            add_balance = [True, True]

    cf_url = f'{PATH}/data/CompanyData/{stock.ticker}/{stock.ticker}_CashFlow.cvs'
    # if cash flow is not empty then get it
    if not os.path.isfile(cf_url):
        add_cashflow = False
    elif os.stat(cf_url).st_size == 0:
        add_cashflow = False
    else:
        operating, investing, financing = stock.get_cashflow()
        add_cashflow = True

    financial_graphs = []

    def is_series_empty(series):
        nills = 0
        for val in series.values:
            if val == "*":
                nills += 1
        if nills == len(series.values):
            return True
        else:
            return False

    if add_income:
        # Income Statement Graph
        if len(revenue) < 6:
            columns = len(revenue)
        else:
            columns = 6
        data = []
        table = []
        if not is_series_empty(revenue):
            data.append(components.make_graph(revenue, '#3DAEA2', 'bar'))
            table.append(revenue)
        if not is_series_empty(operatingIncome):
            data.append(components.make_graph(operatingIncome, '#20639B', 'bar'))
            table.append(operatingIncome)
        if not is_series_empty(netIncome):
            data.append(components.make_graph(netIncome, '#153F5F', 'bar'))
            table.append(netIncome)
        if not is_series_empty(grossMargin):
            data.append(components.make_graph(grossMargin, '#FE4A3B', 'scatter2y'))
            table.append(grossMargin)
        if not is_series_empty(operatingMargin):
            data.append(components.make_graph(operatingMargin, '#C70838', 'scatter2y'))
            table.append(operatingMargin)

        income_statement = html.Div(className='col s12', children=[
            html.H5("ANNUAL INCOME STATEMENT", className="center-align"),
            html.Div(className="divider"),
            html.Div([
                dcc.Graph(
                    id='is_graph',
                    config=gs['config'],
                    figure=go.Figure(
                        data=data,
                        layout=go.Layout(
                            dragmode=False,
                            hovermode=gs['hovermode'],
                            showlegend=gs['showlegend'],
                            autosize=True,
                            xaxis={"type": "category"},
                            yaxis2=dict(
                                overlaying='y',
                                ticksuffix="%",
                                side='right'),
                            margin=go.Margin(l=30, r=30, t=0, b=30)
                        )
                    )
                )
            ], className="col s12 xl6"),
            components.Table(table, html_class='col s12 xl6', columns=columns).make_graph_table(href="financials/is", color_class=["my-green", "my-blue", "my-dark-blue", "my-orange", "my-red"])
        ])
        # make table for income statement. One row for each value in row.
        financial_graphs.append(income_statement)
    if add_balance[0]:
        if len(assets) < 6:
            columns = len(assets)
        else:
            columns = 6
        if add_balance[1]:
            data = [components.make_graph(assets, '#3DAEA2', 'bar'),
                    components.make_graph(liabilities, '#20639B', 'bar'),
                    components.make_graph(debt_ratio, '#FE4A3B', 'scatter2y')
                    ]
            table = [assets, liabilities, debt_ratio]
        else:
            data = [components.make_graph(assets, '#3DAEA2', 'bar'),
                    components.make_graph(liabilities, '#20639B', 'bar')
                    ]
            table = [assets, liabilities]
        # Balance Sheet Graph
        balance_sheet = html.Div(className='col s12 financials-graph', children=[
            html.H5("ANNUAL BALANCE SHEET", className="center-align"),
            html.Div(className="divider"),
            html.Div([
                dcc.Graph(
                    id='bs_graph',
                    config=gs['config'],
                    figure=go.Figure(
                        data=data,
                        layout=go.Layout(
                            dragmode=False,
                            hovermode=gs['hovermode'],
                            showlegend=gs['showlegend'],
                            autosize=True,
                            xaxis={"type": "category"},
                            yaxis2=dict(
                                overlaying='y',
                                ticksuffix="%",
                                side='right'),
                            margin=go.Margin(l=30, r=30, t=0, b=30)
                        )
                    )
                )
            ], className="col s12 xl6"),
            components.Table(table, html_class='col s12 xl6', columns=columns).make_graph_table(href="financials/bs", color_class=["my-green", "my-blue", "my-red"])
        ])
        financial_graphs.append(balance_sheet)

    if add_cashflow:
        if len(financing) < 6:
            columns = len(financing)
        else:
            columns = 6
        if operating is None:
            graph_data = [
                components.make_graph(investing, '#20639B', 'bar'),
                components.make_graph(financing, '#153F5F', 'bar')
            ]
            cashflow_table = components.Table([investing, financing], html_class='col s12 xl6').make_graph_table(['Investing Activities', 'Financing Activities'])
        else:
            graph_data = [
                components.make_graph(operating, '#3DAEA2', 'bar'),
                components.make_graph(investing, '#20639B', 'bar'),
                components.make_graph(financing, '#153F5F', 'bar')
            ]
            cashflow_table = components.Table([operating, investing, financing], html_class='col s12 xl6').make_graph_table(column_name=['Operating Activities', 'Investing Activities', 'Financing Activities'], href="financials/cf", color_class=["my-green", "my-blue", "my-dark-blue"])
        # Cash Flow Graph
        cashflow_graph = html.Div(className='col s12 l6', children=[
            dcc.Graph(
                id='cf_graph',
                config=gs['config'],
                figure=go.Figure(
                    data=graph_data,
                    layout=go.Layout(
                        margin=go.Margin(l=30, r=30, b=30, t=0),
                        dragmode=False,
                        hovermode=gs['hovermode'],
                        showlegend=gs['showlegend'],
                        xaxis={"type": "category"},
                        autosize=True
                        # yaxis=dict(fixedrange=gs['fixedrange']),
                    )
                )
            )
        ])
        cf_html = html.Div(className='col s12 financials-graph', children=[
            html.H5("ANNUAL CASH FLOW ", className="center-align"),
            html.Div(className="divider"),
            cashflow_graph,
            cashflow_table
        ])
        financial_graphs.append(cf_html)

    financials_html = html.Div(className='row', children=financial_graphs)

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
    if os.stat(f'{PATH}/data/CompanyData/{stock.ticker}/{stock.ticker}_KeyRatios.cvs').st_size == 0:
        keyratios_html = html.Div(className='', children=[
            html.H5(f'*Key Ratios for {stock.name} do not exist...')
        ])
    else:
        rev_growth_vals, inc_growth_vals, efficiency_vals, financials_vals, profitability_vals, cashflow_vals, liquidity_vals = stock.get_all_keyratios()
        # print("get_all_keyratios function success")
        del financials_vals
        all_keyratios = [profitability_vals, cashflow_vals, liquidity_vals, efficiency_vals, rev_growth_vals, inc_growth_vals]
        keyratios_name = ["PROFITABILITY", "CASH FLOW", "LIQUIDITY", "EFFICIENCY", "REVENUE GROWTH", "NET INCOME GROWTH"]
        keyratios_startrow = [-1, -1, -1, -1, -1, -2]
        num = 0
        for val in all_keyratios:  # filtering bad data out
            if val == []:  # if list is empty then we don't want to add it.
                all_keyratios.remove(val)
                del(keyratios_name[num])
                del(keyratios_startrow[num])
            num += 1

        keyratios_html = html.Div([
            html.Div([
                html.Div(className='row', children=components.Table(
                    all_keyratios,
                    title=[val for val in keyratios_name],
                    startrow=[val for val in keyratios_startrow]
                ).make_keyratios_table(stock.name)
                )
            ])
        ])
    return keyratios_html

def get_table_statement(stock, load):
    if load == "financials-is":
        df = stock.open_income()
        title = "INCOME STATEMENT"
    elif load == "financials-bs":
        df = stock.open_balance()
        title = "BALANCE SHEET"
    elif load == "financials-cf":
        df = stock.open_cashflow()
        title = "CASH FLOW"
    note = df.index.name
    columns_html = [html.Th()]

    for i in df.columns:
        columns_html.append(html.Th(i, scope="col"))
    df.reset_index(inplace=True)

    body_html = []
    highligted = ["Revenue", "Gross profit", "Operating income", "Net income", "Total current assets", "Total assets", "Total cash", "Total non-current assets", "Total liabilities", "Total current liabilities", "Total non-current liabilities", "Total stockholders' equity", "Total liabilities and stockholders' equity", "Net property, plant and equipment", "Total operating expenses", "Income before taxes", "Net income from continuing operations", "Net cash provided by operating activities", "Net cash used for investing activities", "Net cash provided by (used for) financing activities", "Net change in cash"]
    titles = ["Operating expenses", "Earnings per share", "Weighted average shares outstanding", "Assets", "Liabilities and stockholders' equity", "Cash flows from operating activities", "Cash flows from investing activities", "Cash flows from financing activities", "Free cash flow"]
    subtitles = ["Current assets", "Non-current assets", "Liabilities", "Stockholders' equity"]
    subsubtitles = ["Cash", "Property, plant and equipment", "Current liabilities", "Non-current liabilities"]
    indent = ["Total operating expenses", "Total cash", "Net property, plant and equipment", "Total current liabilities", "Total non-current liabilities"]
    h6 = ["Total assets", "Total liabilities", "Total liabilities and stockholders' equity"]
    df = df.to_dict(orient='records')
    for row in df:
        th_rows = []
        for val in row.values():
            if type(val) == str:  # this is either empty data or the row name.
                if val == "*":  # if it's "*"" just append it
                    th_rows.append(html.Td("-"))
                else:  # this is the row name and we should have that as the first column in the row
                    if val in highligted:
                        if val == "Net income" and load == "financials-cf":
                            th_rows.insert(0, html.Td(val.title(), className='indent'))
                        elif val in indent:
                            th_rows.insert(0, html.Th(val.title(), className='indent', scope='row'))
                        elif val in h6:
                            th_rows.insert(0, html.Th(html.H6(val.title(), className='bold'), scope='row'))
                        else:
                            th_rows.insert(0, html.Th(val.title(), scope='row'))
                    elif val in titles:
                        th_rows = [html.Th(val)]
                    else:
                        th_rows.insert(0, html.Td(val.title(), className='indent'))
            else:  # this is normal data and gets appended.
                val = millify.prettify(val)
                val = str(val)
                if val[-2:] == ".0":
                    val = val.replace(".0", "")
                th_rows.append(html.Td(val))

        title_name = str(th_rows[0].children).lower()
        title_name = title_name[0].upper() + title_name[1:]
        if title_name in titles:
            if title_name == "Operating expenses":
                html_row = html.Div(html.H6(f'{title_name.title()}', className="bold"))
            elif title_name == "Free cash flow":  # check if its the title or the row
                if th_rows[1].children == "-" and th_rows[-1].children == "-":
                    html_row = html.Div(html.H6(f'{title_name.title()}', className="bold"), className="top-margin25")
                else:
                    html_row = html.Tr(th_rows)
            else:
                html_row = html.Div(html.H6(f'{title_name.title()}', className="bold"), className="top-margin25")
        elif title_name in subtitles:
            html_row = html.Div(html.P(f'{title_name.title()}', className="bold"), className="top-margin25")
        elif title_name in subsubtitles:
            html_row = html.Div(html.P(f'{title_name.title()}', className="bold indent"))
        else:
            html_row = html.Tr(th_rows)
        body_html.append(html_row)
    financial_statement_html = html.Div([
        html.Div([
            html.Div([
                html.H5(title, className="center-align"),
                html.Div(className='divider'),
                html.P(note),
                html.Table([
                    html.Thead(
                        html.Tr(columns_html)
                    ),
                    html.Tbody(body_html)
                ], className="highlight")
            ], className='col s12')
        ], className='row')
    ], className='section')
    return financial_statement_html

def get_graph_key_stats_section(stock):
    if stock.past_prices_close != "*":
        if stock.use_data == "daily":
            btns = [{'label': 'Close', 'value': 3},
                    {'label': 'High', 'value': 1},
                    {'label': 'Low', 'value': 2}]
        elif stock.use_data == "adj":
            btns = [{'label': 'Close', 'value': 3},
                    {'label': 'High', 'value': 1},
                    {'label': 'Low', 'value': 2},
                    {'label': 'Adjusted', 'value': 4}]
        section_one_html = html.Div([  # section div
            html.Div([  # row div
                html.Div([
                    html.Div(className="divider"),
                    html.H5(f"STOCK PERFORMANCE ({stock.stock_currency})", className="center-align"),
                    html.Div([  # col 10 for graph
                        dcc.Graph(id='stock_graph', config=gs['config'])
                    ], className='col s11'),
                    html.Div([  # col-2 for checklist menu and toggle switch
                        # daq.ToggleSwitch(id="toggle_graph_type", value=True, vertical=True, label="Change to"),
                        dcc.Checklist(  # checklist for graph settings
                            id='dropdown_graph_options',
                            className="",
                            options=btns,
                            value=[3],
                            labelClassName="btn stock-checkbox"
                        )
                    ], className='col s1'),
                    get_stock_growth(stock),  # Stock growth section
                ], className='col l9 push-l3 s12'),
                html.Div([  # key statistics table col 4
                    html.Div(className="divider"),
                    html.H5("KEY INFORMATION", className="center-align"),
                    components.table_keystats(stock)
                ], className='col l3 pull-l9 s8 offset-s2'),
                # insert key stat table here
            ], className='row'),
        ], className='section')
    else:  # When there is no data for the stock's price
        section_one_html = html.Div([  # section div
            html.Div([  # row div
                html.Div([
                    html.Div(className="divider"),
                    html.H5(f"STOCK PERFORMANCE ({stock.stock_currency})", className="center-align"),
                    html.Div([
                        html.H2("Oops!"),
                        html.H6(f"There's been an error retrieving the historical market prices for {stock.name}")
                    ], className="center-align"),
                    html.Div([  # key statistics table col 4
                        html.Div(className="divider"),
                        html.H5("KEY INFORMATION", className="center-align"),
                        components.table_keystats(stock)
                    ], className='col l4 s8')
                ])
                # insert key stat table here
            ], className='row'),
        ], className='section')
    return section_one_html

def get_valuation(stock):
    return html.H5("Coming soon!", className="center-align bold", style={"margin-top": "7em"})

def get_news(stock):
    if "B" == stock.name[-1]:
        name = stock.name.replace(" B", "")
    elif "A" == stock.name[-1]:
        name = stock.name.replace(" A", "")
    elif " " in stock.name:
        name = stock.name.replace(" ", "%20")
    else:
        name = stock.name
    today = str(dt.date.today())
    r = requests.get(f'https://oasm.finanstilsynet.dk/dk/soegmeddelelseresultat.aspx?headline=&name={name}*&RealAnnouncerCVR=&CVRnumber=&announcmentsId=&informationTypeId=-1&languageId=-1&nationality=-1&AnnouncementTypeId=&pubDateFrom=2010-01-01%2000:00&pubDateTo={today}%2023:59&index=1&sindex=1', timeout=10)
    soup = bs.BeautifulSoup(r.text, 'lxml')
    table_rows = soup.find('table', {'class': 'result'}).find_all("tbody")
    translations = {"Annual document (list of published information)": "Årligt dokument",
                    "Annual financial report": "Årsrapport",
                    "Half-yearly financial report": "Halvårsrapport",
                    "Home member state": "Hjemland",
                    "Information about shareholders": "Oplysninger om aktionærer",
                    "Inside information": "Intern viden",
                    "Interim management statement": "Periode meddelse",
                    "Net asset value (inside information)": "Indre værdi",
                    "Own shares": "Egne aktier",
                    "Payments to governments": "Betalinger til myndigheder",
                    "Prospectus": "Prospekter",
                    "Prospectus (small)": "Prospekter (små)",
                    "Quaterly financial report": "Kvartalsrapport",
                    "Related party transactions": "Ledende medarbejderes og nærtståendes transaktioner",
                    "Rights attached to securities": "Rettigheder knyttet til værdipapirer",
                    "Supplemental information": "Supplerende oplysninger",
                    "Takeover bid": "Overtagelsesmeddelse",
                    "Total voting rights": "Antal stemmerettigheder",
                    "Short selling": "Shortselling"}
    body = []
    for row in table_rows:
        tr = row.find("tr", {"class": "detail"})
        all_td = tr.find_all("td")
        date = all_td[0].text
        time = all_td[1].text
        title = all_td[2].find("a").text
        title_link = all_td[2].find("a")["href"]
        publisher = all_td[3].text
        news_type = all_td[4].text
        for english, danish in translations.items():
            if danish in news_type:
                news_type = english
        news_type = news_type.title()
        body.append(html.Tr([
            html.Td(date), html.Td(time), html.Th(html.A(title, href=f"https://oasm.finanstilsynet.dk{title_link}")), html.Td(publisher), html.Td(news_type)]))

    columns_html = [html.Th("Date", scope='col'),
                    html.Th("Time", scope='col'),
                    html.Th("Announcement", scope='col'),
                    html.Th("Published By", scope='col'),
                    html.Th("Type", scope='col')]
                    # html.Th("Stock price", scope='col')]

    news_html = html.Div([
        html.Div([
            html.Div([
                html.H5("NEWS AND ANNOUNCEMENTS", className="center-align"),
                html.Div(className='divider'),
                html.Table([
                    html.Thead(
                        html.Tr(columns_html)
                    ),
                    html.Tbody(body)
                ], className="highlight centered")
                # Create table with following columns: Date, Time, Title, Published by, Type, Price
            ], className='col s12')
        ], className='row')
    ], className='section')
    return news_html

def get_tabs_navbar(stock, load):
    if load == "financials":
        ul = html.Ul([
            html.Li([
                html.A(["OVERVIEW"], href=f'/company/{stock.ticker}', className="black-text")
            ]),
            html.Li([
                html.A(["FINANCIALS"], href='#', className="black-text")
            ], className='active'),
            html.Li([
                html.A(["RATIOS"], href=f'/company/{stock.ticker}/ratios', className="black-text")
            ]),
            html.Li([
                html.A(["VALUATION"], href=f'/company/{stock.ticker}/valuation', className="black-text")
            ]),
            html.Li([
                html.A(["NEWS"], href=f'/company/{stock.ticker}/news', className="black-text")
            ]),

        ])
    elif load == "ratios":
        ul = html.Ul([
            html.Li([
                html.A(["OVERVIEW"], href=f'/company/{stock.ticker}', className="black-text")
            ]),
            html.Li([
                html.A(["FINANCIALS"], href=f'/company/{stock.ticker}/financials', className="black-text")
            ]),
            html.Li([
                html.A(["RATIOS"], href='#', className="black-text")
            ], className='active'),
            html.Li([
                html.A(["VALUATION"], href=f'/company/{stock.ticker}/valuation', className="black-text")
            ]),
            html.Li([
                html.A(["NEWS"], href=f'/company/{stock.ticker}/news', className="black-text")
            ]),

        ])
    elif load == "valuation":
        ul = html.Ul([
            html.Li([
                html.A(["OVERVIEW"], href=f'/company/{stock.ticker}', className="black-text")
            ]),
            html.Li([
                html.A(["FINANCIALS"], href=f'/company/{stock.ticker}/financials', className="black-text")
            ]),
            html.Li([
                html.A(["RATIOS"], href=f'/company/{stock.ticker}/ratios', className="black-text")
            ]),
            html.Li([
                html.A(["VALUATION"], href='#', className="black-text")
            ], className='active'),
            html.Li([
                html.A(["NEWS"], href=f'/company/{stock.ticker}/news', className="black-text")
            ]),

        ])
    elif load == "news":
        ul = html.Ul([
            html.Li([
                html.A(["OVERVIEW"], href=f'/company/{stock.ticker}', className="black-text")
            ]),
            html.Li([
                html.A(["FINANCIALS"], href=f'/company/{stock.ticker}/financials', className="black-text")
            ]),
            html.Li([
                html.A(["RATIOS"], href=f'/company/{stock.ticker}/ratios', className="black-text")
            ]),
            html.Li([
                html.A(["VALUATION"], href=f'/company/{stock.ticker}/valuation', className="black-text")
            ]),
            html.Li([
                html.A(["NEWS"], href='#', className="black-text")
            ], className='active'),

        ])
    elif load == "financials-is" or load == "financials-bs" or load == "financials-cf":
        ul = html.Ul([
            html.Li([
                html.A(["OVERVIEW"], href=f'/company/{stock.ticker}', className="black-text")
            ]),
            html.Li([
                html.A(["FINANCIALS"], href=f'/company/{stock.ticker}/financials', className="black-text")
            ], className='active'),
            html.Li([
                html.A(["RATIOS"], href=f'/company/{stock.ticker}/ratios', className="black-text")
            ]),
            html.Li([
                html.A(["VALUATION"], href=f'/company/{stock.ticker}/valuation', className="black-text")
            ]),
            html.Li([
                html.A(["NEWS"], href=f'/company/{stock.ticker}/news', className="black-text")
            ]),

        ])
    else:
        ul = html.Ul([
            html.Li([
                html.A(["OVERVIEW"], href='#', className="black-text")
            ], className='active'),
            html.Li([
                html.A(["FINANCIALS"], href=f'{stock.ticker}/financials', className="black-text")
            ]),
            html.Li([
                html.A(["RATIOS"], href=f'/company/{stock.ticker}/ratios', className="black-text")
            ]),
            html.Li([
                html.A(["VALUATION"], href=f'{stock.ticker}/valuation', className="black-text")
            ]),
            html.Li([
                html.A(["NEWS"], href=f'/company/{stock.ticker}/news', className="black-text")
            ]),

        ])
    tabs_html = html.Div([html.Div([  # row div
        html.Div([  # col 12 div
            html.H4(f'{stock.name}', className='center-align'),
        ], className="col s12"),
        html.Nav([
            html.Div([ul], className='nav-wrapper')], className="navbar-basic"),
    ], className="col s12")], className="row margin-bot0")

    return tabs_html


# the final layout that adds all of the components together.
def companyLayout(ticker, name, isin, sector, stock_currency, load):
    stock = usedata.Stock(ticker, name, isin, sector, stock_currency)
    # html layout depending on url
    if load == "financials":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_financial_graphs(stock)
        ])
    elif load == "valuation":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_valuation(stock)
        ])
    elif load == "ratios":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_keyratios_table(stock)
        ])
    elif load == "news":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_news(stock)
        ])
    elif load == "financials-is":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_table_statement(stock, load)
        ])
    elif load == "financials-bs":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_table_statement(stock, load)
        ])
    elif load == "financials-cf":
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_table_statement(stock, load)
        ])
    else:  # overview page
        layout = html.Div([
            dcc.Location(id='url2', refresh=False),
            get_tabs_navbar(stock, load),
            get_graph_key_stats_section(stock)
            # html.Br(),
            # get_financial_graphs(stock),  # Financial graphs section
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
     # Input('toggle_graph_type', 'toggle')
     ]
)
def update_graph(value, relayoutData, pathname):  # toggle
    graph = []
    pathname = pathname.upper()

    if isinstance(pathname, str) and pathname.startswith('/COMPANY/'):
        # Ticker should be what comes after company/
        ticker = pathname[9:].upper()
        if "/FINANCIALS" in pathname:
            pass
        elif "/RATIOS" in ticker:
            pass
            # ticker = ticker.replace("/RATIOS", "")
        elif "/VALUATION" in ticker:
            pass
            # ticker = ticker.replace("/VALUATION", "")
        else:
            # Getting the data
            if os.path.isfile(f'{PATH}/data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs') and os.path.isfile(f'{PATH}/data/CompanyData/{ticker}/{ticker}_DailyPrices.cvs'):  # Finding the one with the most recent data
                daily_adj_mtime = os.path.getmtime(f'{PATH}/data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs')
                daily_mtime = os.path.getmtime(f'{PATH}/data/CompanyData/{ticker}/{ticker}_DailyPrices.cvs')
                if daily_mtime > daily_adj_mtime:
                    use_data = "daily"
                elif daily_mtime < daily_adj_mtime:
                    use_data = "adj"
                else:
                    use_data = "adj"
            elif os.path.isfile(f'{PATH}/data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs'):
                use_data = "adj"
            elif os.path.isfile(f'{PATH}/data/CompanyData/{ticker}/{ticker}_DailyPrices.cvs'):
                use_data = "daily"

            if use_data == "adj":
                df = pd.read_csv(f'{PATH}/data/CompanyData/{ticker}/{ticker}_AdjDailyPrices.cvs')
            elif use_data == "daily":
                df = pd.read_csv(f'{PATH}/data/CompanyData/{ticker}/{ticker}_DailyPrices.cvs')
            df.set_index("timestamp", inplace=True)

            def append_graph(name, data, color):
                graph.append(go.Scatter(
                    x=df.index,
                    y=data,
                    name=name,
                    line=dict(color=color),
                    mode="lines",
                ))
            if use_data == "adj":
                graphValues = {1: ['High', df.high, '#3DAEA2'], 2: ['Low', df.low, '#C70838'], 3: ['Close', df.close, "#20639B"], 4: ['Adj. Close', df.adjusted_close, '#153F5F']}
            elif use_data == "daily":
                graphValues = {1: ['High', df.high, '#3DAEA2'], 2: ['Low', df.low, '#C70838'], 3: ['Close', df.close, "#20639B"]}
            for val in value:
                append_graph(graphValues[val][0], graphValues[val][1], graphValues[val][2])

            today = dt.date.today()
            yearago = today - dt.timedelta(days=184)
            startdict = {'autosize': True}
            autorange = {'xaxis.autorange': True}

            # print('RelayoutData: ', relayoutData)

            # Default. When the data is default set it to show data one year from today
            if relayoutData == startdict or relayoutData is None:
                startdate = yearago
                enddate = today

            # When 'all' button is pressed.
            elif relayoutData == autorange:
                startdate = df.index[-1]
                enddate = df.index[0]

            # When user is using the other buttons.
            # Relayout data is  either a Dict with 2 keys or 4.
            elif len(relayoutData) in [2, 4]:
                startdate = relayoutData['xaxis.range[0]']
                enddate = relayoutData['xaxis.range[1]']

            else:
                startdate = relayoutData['xaxis.range'][0]
                enddate = relayoutData['xaxis.range'][1]

            # End date has to be a dt.date obj.
            if isinstance(enddate, dt.date) is False:
                # if end date is a string then convert it to a date obj.
                if isinstance(enddate, str):
                    enddate = dt.datetime.strptime(enddate[:10], '%Y-%m-%d').date()

                # if end date is a datetime obj then convert it to a date obj.
                if isinstance(enddate, dt.datetime):
                    enddate = enddate.date()

            # Start date has to be a dt.date obj.
            if isinstance(startdate, dt.date) is False:
                # if start date is a string then convert it to a date obj.
                if isinstance(startdate, str):
                    startdate = dt.datetime.strptime(startdate[:10], '%Y-%m-%d').date()

                # if start date is a datetime obj then convert it to a date obj.
                elif isinstance(startdate, dt.datetime):
                    startdate = startdate.date()

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

            # adding the volume
            # graph.append(go.Bar(
            #     x=df.index,
            #     y=df.volume,
            #     opacity=0.5,
            #     marker=dict(color="#FFC201"),
            #     yaxis='y2',
            #     name='volume'
            # ))
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
            rangemax = rangemax * 1.05  # making the maximum value 5% bigger, so there's a small margin
            rangemin = df.low.min()

            # for the volume in rangeslider
            # rangemaxy2 = df.volume.max()
            # rangemaxy2 = rangemaxy2 * 1.05  # making the maximum value 5% bigger, so there's a small margin
            # rangeminy2 = df.volume.min()

            return {
                'data': graph,
                'layout': go.Layout(
                    # title="Chart",
                    height=700,
                    margin=go.Margin(
                        l=25,
                        r=0,
                        b=0,
                        t=0,
                        pad=0),
                    yaxis=dict(
                        range=[minval, maxval],
                        overlaying='y2',
                    ),
                    # yaxis2=dict(
                    #     # overlaying='y',
                    #     side='right'),
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
                            # yaxis2=dict(
                            #     range=[rangeminy2, rangemaxy2],
                            #     rangemode='fixed'
                            # ),
                            range=[lastdataDate, today]
                        ),
                        type='date'
                    ),
                    showlegend=False,
                    dragmode='pan'
                )
            }
            # elif toggle is True:
            #     trace = go.Candlestick(
            #         x=df.index,
            #         open=df.open,
            #         high=df.high,
            #         low=df.low,
            #         close=df.close,
            #         increasing={'line': {'color': "#3DAEA2"}},
            #         decreasing={'line': {'color': "#C70838"}}
            #     )
            #     return {
            #         "data": [trace],
            #         "layout": go.Layout(
            #             xaxis={'rangeslider': {'visible': False}, 'autorange': "reversed"},
            #             showlegend=False,
            #             dragmode='pan'
            #         )
            #     }
