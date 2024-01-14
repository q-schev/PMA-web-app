"""
Example of the register_page defaults
"""

from dash import html, Input, Output, dash_table

import dash
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H1('Terminals'),
    html.Div(id='terminal-input'),
])


def parse_input(data):
    terminals = data['terminals']
    terminals_df = pd.DataFrame.from_dict(terminals)
    terminals_df = terminals_df.drop(
        columns=['externalId', 'openingTimes', 'position'])

    return html.Div([
        dash_table.DataTable(
            terminals_df.to_dict('records'),
            [{'name': i, 'id': i} for i in terminals_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'green',
                'fontWeight': 'bold'
            },
        ),
    ])


@dash.callback(
    Output('terminal-input', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def update_input(data):
    if data is None or len(data) == 0:
        return html.H3('No input file uploaded yet')
    else:
        return parse_input(data)
