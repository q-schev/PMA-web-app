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
            id='schedule-table',
            data=vessels_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in vessels_df.columns],
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


@dash.callback(
    Output('store-input', 'data', allow_duplicate=True),
    Input('schedule-table', 'data'),
    Input('store-input', 'data'),
    prevent_initial_call=True
)
def update_input(table_data, input_data):
    if input_data is None or len(input_data) == 0:
        return dash.no_update
    else:
        for table_stop in table_data:
            for input_vessel in input_data['vessels']:
                if input_vessel['id'] == table_stop['Barge']:
                    for input_stop in input_vessel['stops']:
                        if input_stop['terminalId'] == str(table_stop['Location']):
                            n_load_orders = len(input_stop['loadOrders'])
                            n_discharge_orders = len(input_stop['dischargeOrders'])
                            n_load_orders_table = table_stop['Number of load containers']
                            n_discharge_orders_orders_table = table_stop['Number of discharge containers']
                            if (n_load_orders == n_load_orders_table and
                                    n_discharge_orders == n_discharge_orders_orders_table):
                                input_stop['timeWindow']['startDateTime'] = str(table_stop['Planned arrival'])
                                input_stop['timeWindow']['endDateTime'] = str(table_stop['Planned departure'])
                                if input_stop['fixedStop'] != table_stop['Fixed stop']:
                                    print('difference')
                                if isinstance(table_stop['Fixed stop'], bool):
                                    input_stop['fixedStop'] = table_stop['Fixed stop']
                                else:
                                    if table_stop['Fixed stop'].lower() == 'true':
                                        input_stop['fixedStop'] = True
                                    elif isinstance(table_stop['Fixed stop'].lower(), str):
                                        input_stop['fixedStop'] = False

        return input_data
