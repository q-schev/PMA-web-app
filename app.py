import dash
from dash import html, Dash, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

dash.register_page("home", layout="We're home!", path="/")

navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="More Pages",
    ),
    brand="PMA web app",
    color="primary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [
        dcc.Store(id='store-input', storage_type='session'),
        dcc.Store(id='store-output', storage_type='session'),
        navbar,
        dbc.Row([
            dbc.Col(width=3),  # A fake col to keep the title in center no matter what...
            dbc.Col(
                html.H1(children=['PMA', html.Sup('TM'), ' web app by ']),
                width=3,
                style={
                    'textAlign': 'right',
                }),
            dbc.Col(
                html.Div(
                    html.Img(src=dash.get_asset_url('cofano.png')),
                    style={'float': 'left'}
                ),
                width=3,
            )
        ], justify='start'),
        dash.page_container,

    ],
    className="dbc",
    fluid=True,
)

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
