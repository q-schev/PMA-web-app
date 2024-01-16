"""
Example of the register_page defaults
"""

from dash import html, Input, Output, dash_table

import dash
import pandas as pd

dash.register_page(__name__)

layout = html.Div([
    html.H1('Vessels'),
    html.Div(id='vessel-input'),
])


def parse_input(vessels):
    # vessels_df = pd.DataFrame(
    #     columns=['Barge', 'TEU capacity', 'Weight capacity', 'Reefer capacity', 'Dangerous goods capacity',
    #              'Penalty per sailed km', 'Used penalty per day', 'Active times per day', 'Forbidden terminals'])
    vessels_df = pd.DataFrame(
        columns=['Barge', 'TEU capacity', 'Weight capacity', 'Reefer capacity', 'Dangerous goods capacity',
                 'Penalty per sailed km', 'Forbidden terminals'])
    for vessel in vessels:
        new_entry = pd.DataFrame.from_dict({'Barge': [vessel['id']], 'TEU capacity': [vessel['capacityTEU']],
                                            'Weight capacity': [vessel['capacityWeight']],
                                            'Reefer capacity': [vessel['capacityReefer']],
                                            'Dangerous goods capacity': [vessel['capacityDangerGoods']],
                                            'Penalty per sailed km': [vessel['kilometerCost']],
                                            # 'Used penalty per day': [str(vessel['dayCost'])],
                                            # 'Active times per day': [str(vessel['activeTimes'])],
                                            'Forbidden terminals': [str(vessel['forbiddenTerminals'])]})
        vessels_df = pd.concat([vessels_df, new_entry], ignore_index=True)

    return html.Div([
        dash_table.DataTable(
            id='vessel-table',
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
    Output('vessel-input', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def update_input(data):
    if data is None or len(data) == 0:
        return html.H3('No input file uploaded yet')
    else:
        vessels = data['vessels']
        vessels_layout = parse_input(vessels)
        return vessels_layout


@dash.callback(
    Output('store-input', 'data', allow_duplicate=True),
    Input('vessel-table', 'data'),
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
