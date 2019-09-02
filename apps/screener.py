import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
from server import app

def get_screener():
    # different tabs with data:
    # Always ticker and name row
    # default is sector, market cap, P/E, price (latest), volume (latest)
    # df =
    layout = html.Div([html.Div([
        html.H3(["WE'RE LAUNCHING SOON!"], style={'marginBottom': 0}, className='center-align'),
        html.H5(["Free Stock Data For the Nordic Markets"], style={'marginTop': 0, "paddingRight": "1.5em"}, className='center-align')
        # dash_table.DataTable(
        #     id='criteria-table',
        #     columns=[{"name": "Criteria", "id": "criteria"}, {"name": "Condition", "id": "condition"}, {"name": "Value", "id": "value"}],
        # ),
        # # data=""),
        # dash_table.DataTable(
        #     id='screener-table',
        #     columns=[{"name": "test", "id": "test"}, {"name": "test2", "id": "test2"}],
        #     data=df
        # )
    ], className='row')], className="col s12")
    return layout

# @app.callback(
#     Output('stock_graph', 'figure'),
#     [Input('dropdown_graph_options', 'value'),
#      Input('stock_graph', 'relayoutData'),
#      Input('url2', 'pathname')
#      # Input('toggle_graph_type', 'toggle')
#      ]
# )
# def update_screener_table(value, relayoutData, pathname):  # toggle
#     pass
