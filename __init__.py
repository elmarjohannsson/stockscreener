import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pickle
import os
from server import app
from apps import company, screener
from dataDownloads import save_nasdaqcph_companies
from settings import PATH

# creating the layout
def get_app_layout():
    if not os.path.isfile(f'{PATH}/data/pickles/search.pickle'):  # if the file does not exist we have to create it.
        save_nasdaqcph_companies()
    search = pickle.load(open(f'{PATH}/data/pickles/search.pickle', 'rb'))
    layout = html.Div([
        dcc.Location(
            id='url',
            refresh=False
        ),
        html.Div([
            # START OF HEADER
            html.Header([html.Nav([
                html.Div([  # nav-wrapper myblue class
                    html.A("QUANTZ", href="/", className="brand-logo logo-svg center"),
                    html.Ul([  # nav-mobile
                        html.Li(
                            html.A("About Us", href="about")
                        )
                    ], id="nav-mobile", className="right hide-on-med-and-down")
                ], className='nav-wrapper myblue')
            ])]),
            # START OF BODY CONTENT
            html.Main([
                html.Div([  # class=container - div that contains the whole page
                    html.Div(  # search function
                        dcc.Dropdown(options=[{'label': l[1], 'value': l[0]}
                                              for l in search
                                              ],
                                     id='searchbar',
                                     placeholder='Search for stock'),
                        className='section'),
                    html.Div(id='page-content')  # PAGE CONTENT GETS ADDED IN HERE
                ], className='container')
            ])
        ], className="content"),
        # START OF FOOTER
        html.Footer([
            html.Div([  # container
                html.Div([  # row
                    html.Div([  # col l12
                        html.Div([  # col l4
                            html.A("QUANTZ", href="/", className="logolarge-svg")
                        ], className="col l4"),
                        html.Div([  # col l2 right
                            html.P("© 2019 QUANTZ", className="white-text", style={"bottom": "0", "position": "absolute"})
                        ], className="col l2 right", style={"height": "115px", "position": "relative"})
                    ], className="col s12")
                ], className="row")
            ], className="container")
        ], className="myblue")
    ], className="footer")
    return layout


server = app.server

app.layout = get_app_layout()

@app.callback(Output('url', 'pathname'),
              [Input('searchbar', 'value')])
def change_url(value):
    if isinstance(value, str):
        url = "/company/" + value
        return url

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_pages(pathname):
    pathname = pathname.upper()
    if isinstance(pathname, str) and pathname.startswith('/COMPANY/'):
        # Ticker should be what comes after company/
        ticker = pathname[9:].upper()
        if "/FINANCIALS" in pathname:
            if "/FINANCIALS/IS" in pathname:
                ticker = ticker.replace("/FINANCIALS/IS", "")
                load = "financials-is"
            elif "/FINANCIALS/BS" in pathname:
                ticker = ticker.replace("/FINANCIALS/BS", "")
                load = "financials-bs"
            elif "/FINANCIALS/CF" in pathname:
                ticker = ticker.replace("/FINANCIALS/CF", "")
                load = "financials-cf"
            else:
                ticker = ticker.replace("/FINANCIALS", "")
                load = "financials"
        elif "/RATIOS" in ticker:
            ticker = ticker.replace("/RATIOS", "")
            load = "ratios"
        elif "/VALUATION" in ticker:
            ticker = ticker.replace("/VALUATION", "")
            load = "valuation"
        elif "/NEWS" in ticker:
            ticker = ticker.replace("/NEWS", "")
            load = "news"
        else:
            load = "overview"
        # check if the ticker exists
        universe = pickle.load(open(f'{PATH}/data/pickles/universe_companies.pickle', 'rb'))
        if ticker in universe:
            # get data about stock
            ticker_values = universe[ticker]
            isin = ticker_values[0]
            name = ticker_values[1]
            stock_currency = ticker_values[2]  # currency for trading stock price
            sector = ticker_values[3]
            return company.companyLayout(ticker, name, isin, sector, stock_currency, load)
        # else: ticker is not in universe return search result not found page
    else:
        return screener.get_screener()


if __name__ == '__main__':
    app.run_server(debug=True)
