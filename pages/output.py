"""
Example of the register_page defaults
"""

from dash import html, Input, Output, dash_table, dcc

import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import requests
import polyline
import shapely.geometry
import numpy as np

dash.register_page(__name__)

mapbox_token = 'pk.eyJ1IjoidmlkejkiLCJhIjoiY2xudTE4NnAxMDhwNjJqb2R4azVidmY0ciJ9.xkBMi2PEg1jnC-dZN-7gYA'

fig = go.Figure(go.Scatter(x=[], y=[]))
fig.update_layout(template=None)
fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

layout = html.Div([
    html.H1('Output'),
    html.H3(children='Planning KPIs', style={'textAlign': 'center'}),
    html.Div(id='kpis'),
    html.Br(),
    html.H2(children='Planning board', style={'textAlign': 'center'}),
    html.Div([
        html.Div(
            dcc.Graph(
                id='planning_board',
                figure=fig, ),
        )
    ], style={'overflowX': 'scroll',
              'height': '85vh',
              'width': '99vw'}),
    html.Br(),
    html.Div(id='vessel-dropdown'),
    html.Div(children=[dcc.Graph(
        id='map',
        figure=fig,
        style={'width': '180vh',
               'height': '90vh',
               'display': 'inline-block'}
    ),
    ]),
    html.Br(),
    html.Div(children=[dcc.Graph(
        id='bar-chart',
        figure=fig,
        style={'width': '180vh',
               'height': '90vh',
               'display': 'inline-block'}
    ),
    ]),
    html.Br(),
    html.Div(id='output-data-upload'),
])


def process_input_for_planning_board(data):
    planning = data['routes']
    appended_data = []
    for v in range(len(planning)):
        stops = planning[v]['stops']
        vessel = planning[v]['vessel']
        for stop in stops:
            if len(stop['startTime']) < 19:
                stop['startTime'] = stop['startTime'] + ":00"
            if len(stop['departureTime']) < 19:
                stop['departureTime'] = stop['departureTime'] + ":00"
        df_stops = pd.DataFrame.from_dict(stops)
        df_stops = df_stops.drop(columns=['loadOrders', 'dischargeOrders'])
        df_stops['vessel'] = vessel
        df_stops = df_stops[['vessel'] + [c for c in df_stops if c not in ['vessel']]]
        appended_data.append(df_stops)

    df = pd.concat(appended_data)

    df = df.drop(columns=['reefersOnBoardAfterStop', 'dangerousGoodsOnBoardAfterStop', 'fixedStop', 'fixedAppointment'])
    vessels = df.vessel.unique().tolist()

    for vessel in vessels:
        v = df[df['vessel'] == vessel]
        if (len(v) > 1 and sum(v.iloc[0, -6:]) == 0 and v['teuOnBoardAfterStop'].iloc[0] == 0 and
                v['weightOnBoardAfterStop'].iloc[0] == 0):
            df[df['vessel'] == vessel] = df[df['vessel'] == vessel].iloc[1:, :]
            df = df.dropna()
        rows_to_remove = []
        scope = list(v.index.values)
        scope.pop(0)
        for i in scope:
            if df.iloc[i - 1, 1] == df.iloc[i, 1] and df.iloc[i - 1, 3] == df.iloc[i, 2]:
                rows_to_remove.append(i)
                df.iloc[i - 1, 3] = df.iloc[i, 3]
                df.iloc[i - 1, 4] = df.iloc[i, 4]
                df.iloc[i - 1, 5] = df.iloc[i, 5]
                df.iloc[i - 1, 6] = df.iloc[i - 1, 6] + df.iloc[i, 6]
                df.iloc[i - 1, 7] = df.iloc[i - 1, 7] + df.iloc[i, 7]
                df.iloc[i - 1, 8] = df.iloc[i - 1, 8] + df.iloc[i, 8]
                df.iloc[i - 1, 9] = df.iloc[i - 1, 9] + df.iloc[i, 9]
                df.iloc[i - 1, 10] = df.iloc[i - 1, 10] + df.iloc[i, 10]
                df.iloc[i - 1, 11] = df.iloc[i - 1, 11] + df.iloc[i, 11]
                if i + 1 <= scope[-1]:
                    ind = scope.index(i) + 1
                    scope2 = scope[ind:]
                    for j in scope2:
                        if df.iloc[i - 1, 1] == df.iloc[j, 1] and df.iloc[i - 1, 3] == df.iloc[j, 2]:
                            df.iloc[i - 1, 3] = df.iloc[j, 3]
                            df.iloc[i - 1, 4] = df.iloc[j, 4]
                            df.iloc[i - 1, 5] = df.iloc[j, 5]
                            df.iloc[i - 1, 6] = df.iloc[i - 1, 6] + df.iloc[j, 6]
                            df.iloc[i - 1, 7] = df.iloc[i - 1, 7] + df.iloc[j, 7]
                            df.iloc[i - 1, 8] = df.iloc[i - 1, 8] + df.iloc[j, 8]
                            df.iloc[i - 1, 9] = df.iloc[i - 1, 9] + df.iloc[j, 9]
                            df.iloc[i - 1, 10] = df.iloc[i - 1, 10] + df.iloc[j, 10]
                            df.iloc[i - 1, 11] = df.iloc[i - 1, 11] + df.iloc[j, 11]
    df[df['vessel'] == vessel] = df[df['vessel'] == vessel].drop(index=rows_to_remove)

    # date_format = '%Y-%m-%dT%H:%M:%S'
    # df['startTime'] = pd.to_datetime(df['startTime'], format=date_format)
    # df['departureTime'] = pd.to_datetime(df['departureTime'], format=date_format)
    # df['startTime'] = df['startTime'].astype(str)
    # df['departureTime'] = df['departureTime'].astype(str)
    return df


def create_planning_board(df, data):
    vessels = df.vessel.unique().tolist()
    if len(vessels) > 2:
        alpha = len(vessels)
    elif len(vessels) == 2:
        alpha = 6
    planning_board_fig = px.timeline(df, x_start='startTime', x_end='departureTime', y='vessel', color='terminalId',
                                     hover_data=["loading20", "loading40", "loading45", "discharging20",
                                                 "discharging40",
                                                 "discharging45", "teuOnBoardAfterStop", "weightOnBoardAfterStop"],
                                     color_discrete_sequence=px.colors.qualitative.Alphabet, height=alpha * 40,
                                     width=alpha * 600)
    planning_board_fig.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up

    date_format = '%Y-%m-%dT%H:%M:%SZ'
    timestamp = pd.to_datetime(data['timestamp'], format=date_format) + datetime.timedelta(days=2)

    planning_board_fig.add_vline(x=timestamp)
    return planning_board_fig


def load_and_process_kpis(data):
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
    # df.to_excel("json_to_excel.xlsx")

    unplanned = data['unplannedOrders']
    n_unplanned = len(unplanned)
    n_planned = df['discharging20'].sum() + df['discharging40'].sum() + df['discharging45'].sum()

    vessels = df['vessel'].unique()
    unused = []
    for vessel in vessels:
        for s in reversed(range(len(df[df['vessel'] == vessel]))):
            if not df[df['vessel'] == vessel]['fixedStop'].iloc[s]:
                if (df[df['vessel'] == vessel]['loading20'].iloc[s] > 0 or
                        df[df['vessel'] == vessel]['loading40'].iloc[s] > 0 or
                        df[df['vessel'] == vessel]['loading45'].iloc[s] > 0):
                    break
                else:
                    if df[df['vessel'] == vessel]['fixedStop'].iloc[s - 1]:
                        unused.append(vessel)
            elif s == len(df[df['vessel'] == vessel]) - 1:
                unused.append(vessel)

    n_stops = 0
    for r in range(1, len(df)):
        vessel1 = df['vessel'].iloc[r - 1]
        vessel2 = df['vessel'].iloc[r]
        if vessel1 == vessel2:
            terminal1 = df['terminalId'].iloc[r - 1]
            terminal2 = df['terminalId'].iloc[r]
            if terminal1 != terminal2:
                n_stops = n_stops + 1
    n_stops = n_stops + len(vessels)

    distance_sailed = 0
    for i in range(len(data['routes'])):
        distance_sailed = distance_sailed + data['routes'][i]['distanceSailed']

    # planning_time = end - start
    planning_time = 0

    return n_planned, n_unplanned, unused, n_stops, distance_sailed, planning_time, unplanned


def parse_output(data):
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


def create_map(terminal_data, routes, vessel_name):
    terminals = []
    for route in routes:
        for stop in route['stops']:
            terminal_id = stop['terminalId']
            if terminal_id not in terminals:
                terminals.append(terminal_id)

    map_data = pd.DataFrame(columns=['Terminal', 'Longitude', 'Latitude', 'Color'])
    for i in range(len(terminals)):
        name = terminals[i]
        if name not in map_data['Terminal'].values:
            for terminal in terminal_data:
                if terminals[i] == terminal['terminalId']:
                    lat = terminal['position']['latitude']
                    lon = terminal['position']['longitude']
                    map_data.loc[len(map_data)] = [name, lon, lat, 'blue']

    map_fig = go.Figure(
        go.Scattermapbox(
            lat=map_data['Latitude'],
            lon=map_data['Longitude'],
            text=map_data['Terminal'],
            textposition='top right',
            mode='markers+text',
            marker=go.scattermapbox.Marker(
                color=map_data['Color']

            )
        )
    )
    username = 'reader1'
    password = 'retc42mGp1gZSVL'
    auth = (username, password)
    j = 0
    k = 0
    for route in routes:
        if route['vessel'] == vessel_name:
            for stop in route['stops']:
                current_terminal = stop['terminalId']
                lon1 = float(map_data[map_data['Terminal'] == current_terminal]['Longitude'])
                lat1 = float(map_data[map_data['Terminal'] == current_terminal]['Latitude'])

                if j > 0:
                    lon2 = previous[0]
                    lat2 = previous[1]
                    previous_terminal = previous[2]
                    url = f"https://idcp-ship.cofanoapps.com/getroutes?from={lat1},{lon1}&to={lat2},{lon2}"
                    req = requests.get(url=url, auth=auth)
                    info = req.json()
                    if len(info) == 1:
                        if lon2 != lon1:
                            map_fig.add_trace(go.Scattermapbox(mode='lines',
                                                               lon=[lon2, lon1],
                                                               lat=[lat2, lat1],
                                                               line=dict(
                                                                   width=1,
                                                                   color=px.colors.sequential.Plasma[k]
                                                               ),
                                                               name='{0} - {1}'.format(str(previous_terminal),
                                                                                       str(current_terminal))
                                                               ))
                    else:
                        route = info['Routes'][0]
                        coded_polyline = route['Polyline']
                        line = polyline.decode(coded_polyline)
                        lats = []
                        lons = []
                        line = shapely.LineString(line)
                        x, y = line.xy
                        lats = np.append(lats, x)
                        lons = np.append(lons, y)
                        lats = np.append(lats, None)
                        lons = np.append(lons, None)
                        map_fig.add_trace(go.Scattermapbox(mode='lines',
                                                           lat=lats,
                                                           lon=lons,
                                                           line=dict(
                                                               width=1,
                                                               color=px.colors.sequential.Plasma[k]
                                                           ),
                                                           name='{0} - {1}'.format(str(previous_terminal),
                                                                                   str(current_terminal))
                                                           ))

                previous = [lon1, lat1, current_terminal]

                k += 1
                if k == len(px.colors.sequential.Plasma):
                    k = 0
                j += 1

    map_fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,  #
            center=go.layout.mapbox.Center(lat=52, lon=5),
            zoom=6
        )
    )

    return map_fig


def get_vessels_from_data(data):
    vessels = []
    fleet = data['vessels']
    for vessel in fleet:
        vessels.append(vessel['id'])
    return vessels


def create_bar_chart(routes):
    no_of_containers_per_teu_per_barge = pd.DataFrame(columns=['Barge', 'Location', 'TEU'])
    for route in routes:
        barge = route['vessel']
        for stop in route['stops']:
            location = stop['terminalId']
            teu_loading = stop['loading20'] + 2 * stop['loading40'] + 2.25 * stop['loading45']
            teu_discharging = stop['discharging20'] + 2 * stop['discharging40'] + 2.25 * stop['discharging45']
            teu_total = teu_loading + teu_discharging
            mask = (no_of_containers_per_teu_per_barge.iloc[:, 0] == barge) & (
                        no_of_containers_per_teu_per_barge.iloc[:, 1] == location)
            if mask.any():
                # Find the index of the first matching row
                index_of_first_match = no_of_containers_per_teu_per_barge.index[mask].tolist()[0]

                # Set the value of the third column for the matching row
                new_teu_total = no_of_containers_per_teu_per_barge.at[
                                    index_of_first_match, no_of_containers_per_teu_per_barge.columns[2]] + teu_total
                no_of_containers_per_teu_per_barge.at[
                    index_of_first_match, no_of_containers_per_teu_per_barge.columns[2]] = new_teu_total
            else:
                no_of_containers_per_teu_per_barge.loc[len(no_of_containers_per_teu_per_barge)] = [barge, location,
                                                                                               teu_total]
    no_of_containers_per_teu_per_barge_without_MCT = no_of_containers_per_teu_per_barge[no_of_containers_per_teu_per_barge.iloc[:, 1] != 'MCT']
    bar_fig = px.bar(no_of_containers_per_teu_per_barge_without_MCT, x='Barge', y='TEU', color='Location',
                     title='Moves (in TEU) for each barge per terminal')

    return bar_fig


@dash.callback(
    Output('planning_board', 'figure'),
    Input('store-output', 'data'),
    Input('store-input', 'data')
    # prevent_initial_call=True
)
def update_figure(output_data, input_data):
    if output_data is None or len(output_data) == 0:
        return dash.no_update
    else:
        result = process_input_for_planning_board(output_data)
        return create_planning_board(result, input_data)


@dash.callback(
    Output('kpis', 'children'),
    Input('store-output', 'data'),
    # prevent_initial_call=True
)
def show_kpis(data):
    if data is None or len(data) == 0:
        return html.H3('No output file generated yet')
    else:
        n_planned, n_unplanned, unused, n_stops, distance_sailed, planning_time, unplanned = load_and_process_kpis(
            data)

    if len(unused) > 1:
        unused = ", ".join(unused)
    else:
        unused = str(unused)

    to_print = [
        'Created a schedule! Number of containers planned: ' + str(n_planned) + ', Number of unplanned containers: ' +
        str(n_unplanned) + ', Unused barges: ' + str(unused) + ', Total number of stops: ' +
        str(n_stops) + ', Total distance to sail: ' + str(
            distance_sailed) + ' KM' + ', Number of seconds to create schedule: ' + str(round(planning_time)) + '. \n']
    if len(unplanned) > 0:
        unplanned_print = ['\n Unplanned containers: ']
        for u in range(len(unplanned)):
            unplanned_print = unplanned_print + [str(unplanned[u])]
            if u < len(unplanned) - 1:
                unplanned_print = unplanned_print + [", "]
        to_print = to_print + unplanned_print

    return html.Div(to_print)


@dash.callback(
    Output('output-data-upload', 'children'),
    Input('store-output', 'data'),
    # prevent_initial_call=True
)
def update_output(data):
    if data is None or len(data) == 0:
        return html.H3('')
    else:
        return parse_output(data)


@dash.callback(
    Output('vessel-dropdown', 'children'),
    Input('store-input', 'data')
)
def update_graph(data):
    vessels = get_vessels_from_data(data)
    return html.Div(children=[dcc.Dropdown(
        vessels,
        vessels[0],
        id='vessel'
    )])


@dash.callback(
    Output('map', 'figure'),
    Input('store-input', 'data'),
    Input('store-output', 'data'),
    Input('vessel', 'value')
)
def update_graph(input_data, output_data, vessel_name):
    if output_data is None or len(output_data) == 0:
        return dash.no_update
    else:
        return create_map(input_data['terminals'], output_data['routes'], vessel_name)


@dash.callback(
    Output('bar-chart', 'figure'),
    Input('store-output', 'data'),
)
def update_graph(output_data):
    print("Update Graph Callback Called")
    if output_data is None or len(output_data) == 0:
        print("No Output Data")
        return dash.no_update
    else:
        print("Creating Bar Chart")
        bar_fig = create_bar_chart(output_data['routes'])
        print("Bar Chart Created")
        return bar_fig
