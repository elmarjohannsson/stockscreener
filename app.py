import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pickle
import os
from server import app, server
from apps import company
from dataDownloads import save_nasdaqcph_companies

# creating the layout
def get_app_layout():
    if not os.path.isfile('data/pickles/search.pickle'):  # if the file does not exist we have to create it.
        save_nasdaqcph_companies()
    search = pickle.load(open('data/pickles/search.pickle', 'rb'))
    layout = html.Div([
        dcc.Location(
            id='url',
            refresh=False
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.A(href='/', children=html.H2('StockScreener.dk')),
                ], className='column col-3'),
                html.Div([
                    dcc.Dropdown(options=[{'label': l[1], 'value': l[0]}
                                          for l in search
                                          ],
                                 id='searchbar',
                                 placeholder='Enter Company Name or Ticker')
                ], className='column col-3'),
            ], className='columns col-gapless'),
        ], className='container, header'),
        html.Div(id='page-content')
    ])
    return layout


server = server

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
    if isinstance(pathname, str) and pathname.startswith('/company/'):
        # Ticker should be what comes after company/
        ticker = pathname[9:].upper()

        #  check if the ticker exists
        universe = pickle.load(open('data/pickles/universe_companies.pickle', 'rb'))

        if ticker in universe:
            # get data about stock
            ticker_values = universe[ticker]
            isin = ticker_values[0]
            name = ticker_values[1]
            stock_currency = ticker_values[2]  # currency for trading stock price
            sector = ticker_values[3]
            return company.companyLayout(ticker, name, isin, sector, stock_currency)
        # index site should be returned here
        # else
        #     return


if __name__ == '__main__':
    app.run_server(debug=True)
