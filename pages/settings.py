import dash
import dash_bootstrap_components as dbc
from dash import html

# dash.register_page(__name__, path='/settings')

print("Settings page opened.")


def serve_layout():
    layout = html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H2(children="Settings", className="mb-2"),),
            ]),

        ])
    ])

    return layout


layout = serve_layout()



