import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import usedata
from server import app
import pandas as pd
from collections import OrderedDict
from settings import PATH
import pickle

def get_screener():
    # different tabs with data:
    # Always ticker and name row
    # default is sector, market cap, P/E, price (latest), volume (latest)
    # df_screener_data =
    df_screener_options = pd.DataFrame(OrderedDict([
        ('category', ['Profitability', "Income Growth", "Financials"]),
        ('criteria', ['ROE Ratio', "YoY Growth, %", "Payout Ratio, %"]),
        ('condition', ["More than", "More than", "More than"]),
        ('value', ["5", "10", "0"])
    ]))

    layout = html.Div([html.Div([
        html.H3(["WE'RE LAUNCHING SOON!"], style={'marginBottom': 0}, className='center-align'),
        html.H5(["Free Stock Data For the Nordic Markets"], style={'marginTop': 0, "paddingRight": "1.5em"}, className='center-align'),
        dash_table.DataTable(  # table for creating filters
            id='criteria-table',
            data=df_screener_options.to_dict('records'),
            columns=[
                {"name": "Category", "id": "category", "presentation": "dropdown"},
                {"name": "Ratio", "id": "criteria", "presentation": "dropdown"},
                {"name": "Condition", "id": "condition", "presentation": "dropdown"},
                {"name": "Value", "id": "value"}
            ],
            # style_table={'overflowX': 'scroll'},
            style_cell_conditional=[
                {'if': {'column_id': 'category'},
                 'width': '35%'},
                {'if': {'column_id': 'criteria'},
                 'width': '35%'},
                {'if': {'column_id': 'condition'},
                 'width': '20%'},
                {'if': {'column_id': 'value'},
                 'width': '10%'},
            ],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(250, 250, 250)',
                }
            ],
            style_header={"textAlign": "center", 'backgroundColor': 'rgb(240, 240, 240)', "fontWeight": "bold"},
            row_deletable=True,
            dropdown={
                "condition": {
                    "options": [
                        {"label": i, "value": i}
                        for i in [
                            "More than",
                            "Equal to",
                            "Less than"
                        ]
                    ]
                },
                "category": {
                    "options": [
                        {"label": i, "value": i}
                        for i in [
                            # "Descriptive",
                            "Financials",
                            "Revenue Growth",
                            "Income Growth",
                            "Efficiency",
                            "Profitability",
                            "Cash Flow",
                            "Liquidity",
                            # "Valuation"
                        ]
                    ]
                }
            },
            dropdown_conditional=[{
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Descriptive'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "Market Cap",
                        "Sector",
                        "30-Day Avg Volume",
                        "Share Price",
                        "Stock Exchange",
                        "Currency",
                        "Shares Outstanding"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Financials'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "EPS, DKK",
                        # "Latest Dividends",
                        "Payout Ratio, %",
                        "Book Value per Share, DKK",
                        "Free Cash Flow, Mill DKK",
                        "Free Cash Flow per Share, DKK"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Income Growth'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "YoY Growth, %",
                        "3-Year Avg Growth, %",
                        "5-Year Avg Growth, %",
                        "10-Year Avg Growth, %"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Revenue Growth'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "YoY Growth, %",
                        "3-Year Avg Growth, %",
                        "5-Year Avg Growth, %",
                        "10-Year Avg Growth, %"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Efficiency'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "Asset Turnover",
                        "Fixed Assets Turnover",
                        "Inventory Turnover",
                        "Receivables Turnover",
                        "Days Inventory",
                        "Days Sales Outstanding",
                        "Payables Period",
                        "Cash Conversion Cycle"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Profitability'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "ROA Ratio",
                        "ROE Ratio",
                        "ROIC Ratio",
                        "Net Margin, %",
                        "Operating Margin, %",
                        "Gross Margin, %",
                        "Tax Rate, %",
                        "Avg Financial Leverage",
                        "Interest Coverage"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Cash Flow'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "YoY Operating Cash Flow Growth, %",
                        "YoY Free Cash Flow Growth, %",
                        "Free Cash Flow / Sales, %",
                        "Free Cash Flow / Net Income",
                        "Cap Ex as a % of Sales",
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Liquidity'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "Current Ratio",
                        "Quick Ratio",
                        "Debt/Equity"
                        # "Financial Leverage"
                    ]
                ]
            }, {
                "if": {
                    'column_id': "criteria",
                    "filter_query": "{category} eq 'Valuation'"
                },
                "options": [
                    {'label': i, 'value': i}
                    for i in [
                        "P/E Ratio",
                        "Enterprise Value"
                    ]
                ]
            }],
            editable=True,
        ),
        html.Button('Add Filter', "add-rows-button", n_clicks=0, className='btn', style={"margin-top": "6px"}),
        html.Div(id='results')
        # The table for displaying the data
        # dash_table.DataTable(
        #     id='screener-table',
        #     columns=[{"name": "test", "id": "test"}, {"name": "test2", "id": "test2"}]
        #     # data=df
        # )
    ], className='row')], className="col s12")
    return layout

@app.callback(
    Output("criteria-table", "data"),
    [Input('add-rows-button', "n_clicks")],
    [State("criteria-table", "data"),
     State("criteria-table", "columns")]
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('results', 'children'),
    [Input('criteria-table', 'data')]
)
def update_screener_table(rows):
    categories = {  # dictionary of category: the names from the site aligned with their .pickle file name
        # "Descriptive": "descriptive.pickle", # I need to create this pickle
        "Financials": {"financials_data.pickle": [
                       {"EPS, DKK": "Earnings Per Share DKK Universal"},  # look into this one? not sure what I should do with the different currencies. All to dkk?
                       # {"Latest Dividends": "Dividends"},  # same as above
                       {"Payout Ratio, %": "Payout Ratio % *"},
                       {"Book Value per Share, DKK": "Book Value Per Share * DKK Universal"},
                       {"Free Cash Flow, Mill DKK": "Free Cash Flow DKK Mil Universal"},  # same as above
                       {"Free Cash Flow per Share, DKK": "Free Cash Flow Per Share * DKK Universal"}  # Same as above
                       ]},
        "Income Growth": {"inc_growth_data.pickle": [
            {"YoY Growth, %": "Year over Year"},
            {"3-Year Avg Growth, %": "3-Year Average"},
            {"5-Year Avg Growth, %": "5-Year Average"},
            {"10-Year Avg Growth, %": "10-Year Average"}
        ]},
        "Revenue Growth": {"rev_growth_data.pickle": [
            {"YoY Growth, %": "Year over Year"},
            {"3-Year Avg Growth, %": "3-Year Average"},
            {"5-Year Avg Growth, %": "5-Year Average"},
            {"10-Year Avg Growth, %": "10-Year Average"}
        ]},
        "Efficiency": {"efficiency_data.pickle": [
                       {"Fixed Assets Turnover": "Fixed Assets Turnover"},
                       {"Days Sales Outstanding": "Days Sales Outstanding"},
                       {"Asset Turnover": "Asset Turnover"},
                       {"Payables Period": "Payables Period"},
                       {"Receivables Turnover": "Receivables Turnover"},
                       {"Days Inventory": "Days Inventory"},
                       {"Cash Conversion Cycle": "Cash Conversion Cycle"},
                       {"Inventory Turnover": "Inventory Turnover"}
                       ]},
        "Profitability": {"profitability_data.pickle": [
            {"ROA Ratio": "Return on Assets %"},
            {"ROE Ratio": "Return on Equity %"},
            {"Net Margin, %": "Net Margin %"},
            {"Gross Margin, %": "Gross Margin %"},
            {"Operating Margin, %": "Operating Margin %"},
            {"Tax Rate, %": "Tax Rate %"},
            {"ROIC Ratio": "Return on Invested Capital %"},
            {"Avg Financial Leverage": "Financial Leverage (Average)"},
            {"Interest Coverage": "Interest Coverage"}
        ]},
        "Cash Flow": {"cashflow_data.pickle": [
            {"Cap Ex as a % of Sales": "Cap Ex as a % of Sales"},
            {"YoY Operating Cash Flow Growth, %": "Operating Cash Flow Growth % YOY"},
            {"YoY Free Cash Flow Growth, %": "Free Cash Flow Growth % YOY"},
            {"Free Cash Flow / Net Income": "Free Cash Flow/Net Income"},
            {"Free Cash Flow / Sales, %": "Free Cash Flow/Sales %"}
        ]},
        "Liquidity": {"liquidity_data.pickle": [
            {"Current Ratio": "Current Ratio"},
            {"Quick Ratio": "Quick Ratio"},
            # {"Financial Leverage": "Financial Leverage"},
            {"Debt/Equity": "Debt/Equity"}
        ]}
        # "Valuation": "valuation.pickle" # I need to create this pickle
    }
    print(rows, type(rows))

    positive = []  # list the companies that fulfill the filters

    row_lists = []  # list containing the rows that is a list of positive companies
    for row in rows:  # checking through the rows and deleting those were all columns are not filled.
        if None or "" in row.values():  # if None or "" in the dict values for the columns then we ignore that row.
            continue
        else:  # for each row get the filter and find the companies that fit this.
            print(row.values(), "ROW VALUES")
            positive_row = []
            category = row["category"]
            criteria = row["criteria"]
            condition = row["condition"]
            value = float(row["value"])
            if category is None:
                pickle_name = None
            else:
                pickle_name = list(categories[category])[0]  # gets the first key from the categories dictionary that stores the pickle file name for the category.
            criteria_name = None
            if pickle_name is None:
                pass
            else:
                for ratio in categories[category][pickle_name]:
                    ratio_criteria = list(ratio)[0]
                    print(criteria, "criteria", ratio_criteria, "ratio_criteria")
                    if ratio_criteria == criteria:
                        criteria_name = ratio
                        print("criteria_name found", criteria_name)
                        continue
            # criteria_name = next((item for item in categories[category][pickle_name] if list(item)[0] == criteria), None)  # gets the criteria_name by finding it in the list of dictionaries.
            # if criteria_name is None:
                # criteria_name = next((item for item in categories[category][pickle_name] if list(item)[0] == criteria), None)
            if criteria_name is None:
                pass
            else:
                criteria_name = criteria_name[criteria]

                data = pickle.load(open(f'{PATH}/data/pickles/{pickle_name}', 'rb'))
                for stock in data[criteria_name].items():  # for every stock in the pickle file we check if the condition holds true, if it does then it gets saved to the positive row.
                    # print("stock", stock)
                    stock_ticker = stock[0]
                    print(stock_ticker)
                    stock_value = float(str(stock[1][0]).replace(",", ""))

                    if condition == "Equal to":
                        if stock_value == value:
                            # print(stock)
                            positive_row.append(stock_ticker)  # add to positive list
                    elif condition == "Less than":
                        if stock_value <= value:
                            positive_row.append(stock_ticker)  # add to positive list
                    elif condition == "More than":
                        if stock_value >= value:
                            positive_row.append(stock_ticker)
                            # positive.append(stock_ticker)  # add to positive lists
                row_lists.append(positive_row)
                # if positive_row len is more than 0 then create else there are no companies that fulfill those criteria
    if len(row_lists) > 0:  # only if there are any criteria ie. more than 0 rows/criteria
        positive = row_lists[0]

        if len(row_lists) > 1:  # when there is more than one row then the positive list should only contain those that fulfill both criteria
            n = 1
            while n < len(row_lists):
                intersect = set(positive).intersection(row_lists[n])
                positive = list(intersect)
                n += 1
        print(positive, "positive list consists of ", len(positive))

    # list of cards for each stock in results
    cards = []
    universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
    for ticker in positive:  # creating html card for each stock in the positive list
        name = universe[ticker][1]
        isin = universe[ticker][0]
        sector = universe[ticker][3]
        stock_currency = universe[ticker][2]

        stock = usedata.Stock(ticker, name, isin, sector, stock_currency)

        df_financials = pd.read_csv(f'{PATH}/data/CompanyData/{ticker}/{ticker}_KeyRatios.cvs', delimiter=',', header=2, skip_blank_lines=True, index_col=[0], nrows=15)
        df_financials.fillna('*', inplace=True)

        eps = df_financials.iloc[5]
        pe = stock.calc_pe_ratio(eps)

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

        # making it pretty
        if ".0" in str(price_latest)[-2:]:
            price_latest = str(price_latest).replace(".0", "")
        if type(pe) is str:
            pe = "-"
        else:
            pe = round(pe, 2)

        # the HTML
        stock_card = html.Div([  # html syntax for each company card.
            html.Div([
                html.Div([
                    html.Span(name, className='card-title'),
                    html.P(f"Price {price_latest} {stock_currency}"),
                    html.P(f"P/E {pe}"),
                    html.P(f"1 Year Return {return_1yr}"),
                    html.P(sector)
                ], className='card-content'),
                html.Div([
                    html.A("See more", href=f'/company/{ticker}')
                ], className='card-action')
            ], className="card")
        ], className="col s12 m6 l4")

        cards.append(stock_card)  # appending them all to a long list

    result_html = html.Div(className='col s12', children=[
        html.H5(f"{len(positive)} RESULTS:", className="center-align"),
        html.Div(className="divider"),
        html.Div(cards)
    ])
    return result_html


if __name__ == "__main__":
    rows = [{'category': 'Descriptive', 'criteria': 'Market Cap', 'condition': 'Equal', 'value': ''}, {'category': 'Growth', 'criteria': 'Exchange', 'condition': 'Less than', 'value': ''}, {'category': 'Profitability', 'criteria': 'Sector', 'condition': 'More than', 'value': ''}]
    update_screener_table(rows)
