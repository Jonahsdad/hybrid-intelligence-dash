from __future__ import annotations
import os
from dash import Dash, dcc, html, Input, Output, State, page_container, callback_context
import dash_bootstrap_components as dbc

BRAND = os.getenv("BRAND", "HYBRID INTELLIGENCE SYSTEMS")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
    title=f"{BRAND} — Dash"
)
server = app.server

app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id="jwt"),
        dcc.Store(id="prefs", storage_type="local"),
        dbc.Navbar(
            dbc.Container([
                html.Div(f"{BRAND}", className="brand"),
                dbc.Nav([
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Crypto", href="/crypto", active="exact"),
                    dbc.NavLink("Status", href="/status", active="exact"),
                    dbc.NavLink("Plans", href="/plans", active="exact"),
                ], className="me-auto"),
                dbc.Input(id="email", placeholder="email", size="sm", style={"width":"200px"}),
                dbc.Input(id="team", placeholder="team",  size="sm", style={"width":"140px","marginLeft":"6px"}),
                dbc.Button("Sign in", id="btn-login", size="sm", className="ms-2", n_clicks=0),
                html.Span(id="login-msg", className="ms-3 small text-muted"),
            ], fluid=True),
            color="dark", dark=True, className="mb-3",
        ),
        page_container
    ], fluid=True, className="p-2"
)

# --- login wiring ---
from dash_app.lib.api import login

@app.callback(
    Output("jwt", "data"),
    Output("login-msg", "children"),
    Input("btn-login", "n_clicks"),
    State("email", "value"),
    State("team", "value"),
    prevent_initial_call=True,
)
def do_login(n, email, team):
    try:
        res = login(email or "", team or "")
        return res.get("token"), f"signed in • {res.get('team')}"
    except Exception:
        return None, "login failed"

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
