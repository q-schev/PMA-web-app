"""
Example of the register_page defaults
"""

from dash import html, Input, Output, dash_table

import dash
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H1('Orders'),
    html.Div(id='message'),
    html.Div(id='order-input'),
])


def parse_input(data):
    orders = data['orders']
    orders_df = pd.DataFrame(
        columns=['orderId', 'containerType', 'TEU', 'weight', 'loadTerminal', 'dischargeTerminal', 'earliestPickUp',
                 'latestPickUp',
                 'earliestDeadline', 'latestDeadline', 'reefer', 'dangerousGoods'])
    for order in orders:
        new_entry = pd.DataFrame.from_dict(
            {'orderId': [order['orderId']], 'containerType': [order['containerType']], 'TEU': [order['TEU']],
             'weight': [order['weight']], 'loadTerminal': [order['loadTerminal']],
             'dischargeTerminal': [order['dischargeTerminal']],
             'earliestPickUp': [order['loadTimeWindow']['startDateTime']],
             'latestPickUp': [order['loadTimeWindow']['endDateTime']],
             'earliestDeadline': [order['dischargeTimeWindow']['startDateTime']],
             'latestDeadline': [order['dischargeTimeWindow']['endDateTime']], 'reefer': [order['reefer']],
             'dangerousGoods': [order['dangerGoods']]})
        orders_df = pd.concat([orders_df, new_entry], ignore_index=True)

    return html.Div([
        dash_table.DataTable(
            orders_df.to_dict('records'),
            [{'name': i, 'id': i} for i in orders_df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            editable=True,
            export_format='xlsx',
            export_headers='display',
        ),
    ])


@dash.callback(
    Output('order-input', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def update_input(data):
    if data is None or len(data) == 0:
        return html.H3('No input file uploaded yet')
    else:
        return parse_input(data)


@dash.callback(
    Output('message', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def update_input_message(data):
    if data is None or len(data) == 0:
        return html.H5('')
    else:
        return html.H5('Takes a few seconds to load..')
