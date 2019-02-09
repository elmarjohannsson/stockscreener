# import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

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
    def __init__(self, values, index=0, title='', columns=4, html_class='column col-4', startrow=-1):
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
        # first culumn header is title (default is nothing).
        th = [html.Th(self.title)]
        # what values to get. Default is -1, so it gets the latest value.
        num = self.startrow
        # make culumns
        for i in range(self.columns):
            # takes the choosen index value and gets it's index values. Default takes the first value in the list and gets the newst value.
            th.append(html.Th(self.values[self.index].index.tolist()[num]))
            num -= 1
        return th

    def make_graph_table(self, column_name=None):
        self.title_num = 0
        table = html.Div(className=self.html_class, children=[
            html.Table(className='table table-striped table-hover', children=[
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
            ], className='bold')
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

        table = html.Table(className='table table-striped table-hover', children=table_content)
        return table

    # # With sector and market for later update.
    # def make_keyratios_table(self):
    #     table_content = [html.Tr([
    #         html.Th(""),
    #         html.Th('name of company', colSpan='4'),
    #         html.Th('sector: name of sector', colSpan='4'),
    #         html.Th('market', colSpan='4')
    #     ])
    #     ]
    #     # Row 2 - secondary columns, headers for values
    #     num = 0
    #     n = self.startrow
    #     for val in self.values:  # val returns a list of pandas series that all use the same header columns.
    #         # print('Index list', self.values[num][self.index].index.tolist())
    #         # print('current num', num)
    #         table_index = html.Tr([
    #             # first is index column
    #             html.Td(self.title[num]),
    #             # next four are for the stock
    #             html.Td(self.values[num][self.index].index.tolist()[n[num]]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 1]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 2]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 3]),
    #             # Next four are for sector
    #             html.Td(self.values[num][self.index].index.tolist()[n[num]]),  # instead of self.values i should be using the sector data.
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 1]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 2]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 3]),
    #             # Next four are for market/comparison with specific company
    #             html.Td(self.values[num][self.index].index.tolist()[n[num]]),  # instead of self.values i should be using the market data.
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 1]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 2]),
    #             html.Td(self.values[num][self.index].index.tolist()[n[num] - 3])
    #         ], className='bold')
    #         table_content.append(table_index)
    #         for v in val:
    #             # print('the value2', v)
    #             table_values = html.Tr([
    #                 # first is index column
    #                 html.Td(v.name.title()),
    #                 # next four are for stock
    #                 html.Td(str(v.get_values()[n[num]]).upper()),
    #                 html.Td(str(v.get_values()[n[num] - 1]).upper()),
    #                 html.Td(str(v.get_values()[n[num] - 2]).upper()),
    #                 html.Td(str(v.get_values()[n[num] - 3]).upper()),
    #                 # Next four are for sector
    #                 html.Td('NaN'),
    #                 html.Td('NaN'),
    #                 html.Td('NaN'),
    #                 html.Td('NaN'),
    #                 # Next four are for market/comparison with specific company
    #                 html.Td('NaN'),
    #                 html.Td('NaN'),
    #                 html.Td('NaN'),
    #                 html.Td('NaN')
    #             ])
    #             table_content.append(table_values)
    #         num += 1

    #     table = html.Table(className='table table-striped table-hover', children=table_content)
    #     return table
