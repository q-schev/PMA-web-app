"""
Example of the register_page defaults
"""

from dash import html, Input, Output, dash_table

import dash
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H1('Input schedule'),
    html.Div(id='input-schedule'),
])


def parse_input(data):
    vessels_df = pd.DataFrame(
        columns=['Barge', 'Location', 'Planned arrival', 'Planned departure', 'Number of load containers',
                 'Number of discharge containers', 'Fixed stop'])
    for vessel in data['vessels']:
        for stop in vessel['stops']:
            new_entry = pd.DataFrame.from_dict({'Barge': [vessel['id']], 'Location': [stop['terminalId']],
                                                'Planned arrival': [stop['timeWindow']['startDateTime']],
                                                'Planned departure': [stop['timeWindow']['endDateTime']],
                                                'Number of load containers': [len(stop['loadOrders'])],
                                                'Number of discharge containers': [len(stop['dischargeOrders'])],
                                                'Fixed stop': [stop['fixedStop']]})
            vessels_df = pd.concat([vessels_df, new_entry], ignore_index=True)

    return html.Div([
        dash_table.DataTable(
            vessels_df.to_dict('records'),
            [{'name': i, 'id': i} for i in vessels_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'blue',
                'fontWeight': 'bold'
            },
            editable=True
        ),
    ])


@dash.callback(
    Output('input-schedule', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def update_input(data):
    if data is None or len(data) == 0:
        return html.H3('No input file uploaded yet')
    else:
        return parse_input(data)
