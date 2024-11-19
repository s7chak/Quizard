import dash_bootstrap_components as dbc
from dash import dcc, dash
from dash import html
from dash.dependencies import Input, Output, State
from dash_iconify import DashIconify

from app import app

read_process_status = ""

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="/home"),
    ],
    nav = True,
    in_navbar = True,
    label = "Explore",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    html.A(
                        dbc.Col(html.Img(src=r"assets/logo.png", height="40px", width="40px")),
                        href="/home",
                        style={"marginRight": "10px", "width": "30px"}
                    ),
                    dbc.Col(html.H3("Quizard", style={"margin": "10px"})),
                ],
                align="center",
                style={"width":"100vw"}
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    # home.layout,
    dash.page_container,
])
