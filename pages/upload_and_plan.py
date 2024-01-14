"""
Example of the register_page defaults
"""

from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc

import dash
import base64
import json
import pandas as pd
import requests
import time
import os

dash.register_page(__name__)

layout = html.Div([
    dbc.Row([
        html.H1('Upload and plan'),
        dbc.Col(
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Planning Input')
                ]),
                style={
                    'width': '99vw',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'borderColor': '#DA680F',
                    'font-weight': 'bold',
                    'textAlign': 'center',
                    'margin': '10px',
                    'cursor': 'pointer',
                    'color': '#DA680F',
                    'background-color': '#0d0c0b',
                },
                multiple=False
            ),
        ),
    ]),
    html.Div(id='barge_list'),
    html.Br(),
    html.Div(children=[
        html.Label('Travel distance (minimization priority)'),
        dcc.Slider(
            id='w1_slider',
            min=0,
            max=1,
            step=0.1,
            marks={str(i / 10): str(i / 10) for i in range(11)},
            value=0.1,
        ),
        html.Label('Number of stops (minimization priority)'),
        dcc.Slider(
            id='w2_slider',
            min=0,
            max=1,
            step=0.1,
            marks={str(i / 10): str(i / 10) for i in range(11)},
            value=0.5,
        ),
        html.Label('Unplanned/late containers (minimization priority)'),
        dcc.Slider(
            id='w3_slider',
            min=0,
            max=1,
            step=0.1,
            marks={str(i / 10): str(i / 10) for i in range(11)},
            value=0.5,
        ),
    ]),
    html.Br(),
    html.Div([
        dbc.Button('Plan', size='lg', id='make-planning', n_clicks=0, style={
            'borderColor': '#DA680F',
            'color': '#DA680F',
            'background-color': '#0d0c0b',
            'font-weight': 'bold'}),
    ], style={'textAlign': 'center'}),
    html.Br(),
    html.Div(id='output-data-upload'),
    # html.Br(),
    # html.Div(id='input-data'),
])


def parse_input(data):
    # timestamp = data['timestamp']

    orders = data['orders']
    orders_df = pd.DataFrame(
        columns=['orderId', 'containerType', 'TEU', 'weight', 'loadTerminal', 'dischargeTerminal', 'earliestPickUp',
                 'latestPickUp',
                 'earliestDeadline', 'latestDeadline', 'reefer', 'dangerousGoods'])
    for order in orders:
        if order['reefer']:
            reefer = 'yes'
        else:
            reefer = 'no'
        if order['dangerGoods']:
            dangerous_goods = 'yes'
        else:
            dangerous_goods = 'no'
        new_entry = pd.DataFrame.from_dict(
            {'orderId': [order['orderId']], 'containerType': [order['containerType']], 'TEU': [order['TEU']],
             'weight': [order['weight']],
             'loadTerminal': [order['loadTerminal']], 'dischargeTerminal': [order['dischargeTerminal']],
             'earliestPickUp': [order['loadTimeWindow']['startDateTime']],
             'latestPickUp': [order['loadTimeWindow']['endDateTime']],
             'earliestDeadline': [order['dischargeTimeWindow']['startDateTime']],
             'latestDeadline': [order['dischargeTimeWindow']['endDateTime']], 'reefer': [reefer],
             'dangerousGoods': [dangerous_goods]})
        orders_df = pd.concat([orders_df, new_entry], ignore_index=True)

    terminals = data['terminals']
    terminals_df = pd.DataFrame.from_dict(terminals)
    terminals_df = terminals_df.drop(
        columns=['externalId', 'handlingTime', 'baseStopTime', 'openingTimes', 'callCost', 'callSizeFine', 'position'])

    vessels_df = pd.DataFrame(
        columns=['Barge', 'Location', 'Planned arrival', 'Planned departure', 'loadOrders', 'dischargeOrders',
                 'fixedStop'])
    for vessel in data['vessels']:
        for stop in vessel['stops']:
            if stop['fixedStop']:
                fixed_stop = 'yes'
            else:
                fixed_stop = 'no'
            # fixedAppointment = stop['fixedAppointment']
            new_entry = pd.DataFrame.from_dict({'Barge': [vessel['id']], 'Location': [stop['terminalId']],
                                                'Planned arrival': [stop['timeWindow']['startDateTime']],
                                                'Planned departure': [stop['timeWindow']['endDateTime']],
                                                'loadOrders': [len(stop['loadOrders'])],
                                                'dischargeOrders': [len(stop['dischargeOrders'])],
                                                'fixedStop': [fixed_stop]})
            vessels_df = pd.concat([vessels_df, new_entry], ignore_index=True)

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
        ),
        html.Br(),
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
        html.Br(),
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


def get_vessels_from_data(data):
    vessels = []
    fleet = data['vessels']
    for vessel in fleet:
        vessels.append(vessel['id'])
    return vessels


def upload_and_send_json(data, barges, w1, w2, w3):
    data = adjust_vessels_json(data, barges)
    data = adjust_penalties_json(data, w1, w2, w3)

    # Send the JSON data as part of a POST request
    response = send_json_data(data)
    return [f'Uploaded JSON Data:\n{json.dumps(data, indent=4)}\n\nResponse:\n{response}']


def adjust_vessels_json(data, barges_selected):
    vessels = data['vessels']
    fleet = []
    for vessel in vessels:
        fleet.append(vessel['id'])
    not_selected = [x for x in fleet if x not in barges_selected]
    st = set(not_selected)
    ind_not_selected = [i for i, e in enumerate(fleet) if e in st]
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    for i in ind_not_selected:
        data['vessels'][i]['kilometerCost'] = 100000
        for day in days:
            data['vessels'][i]['dayCost'][day] = 100000
            data['vessels'][i]['terminalCallCost'][day] = 100000

    loaded_orders_notfixed = []
    for i in ind_not_selected:
        for j in range(len(data['vessels'][i]['stops'])):
            if not data['vessels'][i]['stops'][j]['fixedStop']:
                for k in data['vessels'][i]['stops'][j]['loadOrders']:
                    loaded_orders_notfixed.append(k)
                data['vessels'][i]['stops'][j]['loadOrders'] = []
    for i in ind_not_selected:
        for j in range(len(data['vessels'][i]['stops'])):
            if not data['vessels'][i]['stops'][j]['fixedStop']:
                res = [k for k in data['vessels'][i]['stops'][j]['dischargeOrders'] if
                       k not in loaded_orders_notfixed]
                data['vessels'][i]['stops'][j]['dischargeOrders'] = res
    for i in ind_not_selected:
        for j in range(len(data['vessels'][i]['stops'])):
            if not data['vessels'][i]['stops'][j]['fixedStop']:
                if (len(data['vessels'][i]['stops'][j]['dischargeOrders'])) > 0:
                    data['vessels'][i]['stops'][j]['fixedStop'] = True

    return data


def adjust_penalties_json(data, w1, w2, w3):
    w1 = 10 * w1
    w2 = 2 * w2
    w3 = 2 * w3

    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    for i in range(len(data['vessels'])):
        data['vessels'][i]['kilometerCost'] = w1 * data['vessels'][i]['kilometerCost']
        for day in days:
            data['vessels'][i]['terminalCallCost'][day] = w2 * data['vessels'][i]['terminalCallCost'][day]
    for i in range(len(data['terminals'])):
        data['terminals'][i]['callCost'] = w2 * data['terminals'][i]['callCost']
    for i in range(len(data['orders'])):
        data['orders'][i]['fine'] = w3 * data['orders'][i]['fine']
    return data


# Function to send JSON data as part of a POST request
def send_json_data(data):
    url = f'http://localhost:8080/api/planning'
    # url = f'https://pma-acc.cofanoapps.com/api/planning'
    username = 'cofano'
    password = 'cofano'
    # password = 'cofanopma24601'
    auth = (username, password)
    headers = {'Content-type': 'application/json'}
    r = requests.post(url=url, auth=auth, headers=headers, json=data)

    if r.status_code == 200:
        print("POST request was successful!")
        print("Response data:", r.text)
        start = time.time()
    else:
        print("POST request failed with status code:", r.status_code)
        print("Response data:", r.text)


def import_output_json():
    filename = "C:/Users/quiri/Documents/planning output"
    start_time = time.time()
    k = 0
    file_created = os.path.getmtime(filename)
    while file_created < start_time:
        if k == 0:
            print('File created:')
            print(os.path.getmtime(filename))
            print('Program executed:')
            print(start_time)
        file_created = os.path.getmtime(filename)
        k = k + 1
    end = time.time()
    f = open("planning output", "r")
    imported_output_json = json.load(f)
    print('Imported PMA output')
    return imported_output_json


def parse_contents(data):
    planning = data['routes']
    appended_data = []
    for v in range(len(planning)):
        stops = planning[v]['stops']
        vessel = planning[v]['vessel']
        df_stops = pd.DataFrame.from_dict(stops)
        df_stops = df_stops.drop(columns=['loadOrders', 'dischargeOrders'])
        df_stops['vessel'] = vessel
        df_stops = df_stops[['vessel'] + [c for c in df_stops if c not in ['vessel']]]
        appended_data.append(df_stops)

    df = pd.concat(appended_data)

    return html.Div([
        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'orange',
                'fontWeight': 'bold'
            },
            export_format='xlsx',
            export_headers='display',
        ),
    ])


@dash.callback(
    Output('store-input', 'data'),
    Input('upload-data', 'contents'),
    # prevent_initial_call=True
)
def update_input(contents):
    if contents is None:
        return dash.no_update
    else:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        data = json.loads(decoded)
        return data


@dash.callback(
    Output('input-data', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def update_input(data):
    if data is None:
        return dash.no_update
    else:
        return parse_input(data)


@dash.callback(
    Output('barge_list', 'children'),
    Input('store-input', 'data'),
    # prevent_initial_call=True
)
def barge_checklist(data):
    if data is None or len(data) == 0:
        return html.H3('No input file uploaded yet')
    else:
        vessels = get_vessels_from_data(data)
        return html.Div(children=[
            html.Label('Select vessels to plan'),
            dbc.Checklist(id='checklist', options=vessels, value=vessels, inline=True,
                          label_checked_style={"color": "#DA680F", 'font-weight': 'bold', },
                          input_checked_style={
                              "backgroundColor": "#0d0c0b",
                              "borderColor": "#DA680F",
                          }, style={'textAlign': 'center'})
        ])


@dash.callback(
    Output('store-output', 'data'),
    Input('store-input', 'data'),
    Input('make-planning', 'n_clicks'),
    Input('checklist', 'value'),
    Input('w1_slider', 'value'),
    Input('w2_slider', 'value'),
    Input('w3_slider', 'value'),
    prevent_initial_call=True
)
def update_output(data, n_clicks, barges, w1, w2, w3):
    if n_clicks > 0:
        upload_and_send_json(data, barges, w1, w2, w3)
        return import_output_json()
