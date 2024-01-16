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


@dash.callback(
    Output('store-input', 'data', allow_duplicate=True),
    Input('terminal-table', 'data'),
    Input('store-input', 'data'),
    prevent_initial_call=True
)
def update_input(table_data, input_data):
    if input_data is None or len(input_data) == 0:
        return dash.no_update
    else:
        for table_vessel in table_data:
            for input_vessel in input_data['vessels']:
                if input_vessel['id'] == table_vessel['Barge']:
                    input_vessel['capacityTEU'] = int(table_vessel['TEU capacity'])
                    input_vessel['capacityWeight'] = int(table_vessel['Weight capacity'])
                    input_vessel['capacityReefer'] = int(table_vessel['Reefer capacity'])
                    input_vessel['capacityDangerGoods'] = int(table_vessel['Dangerous goods capacity'])
                    input_vessel['kilometerCost'] = int(table_vessel['Penalty per sailed km'])
                    input_vessel['forbiddenTerminals'] = str(table_vessel['Forbidden terminals'])
        return input_data