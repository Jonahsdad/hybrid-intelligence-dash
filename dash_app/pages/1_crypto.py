from __future__ import annotations
from dash import register_page, html, dcc, Input, Output, State, no_update, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from dash_app.lib.api import forecast, explain, share_create, billing_checkout

register_page(__name__, path="/crypto", name="Crypto")

def layout():
    return dbc.Container([
        html.H4("🔥 Crypto — Flagship"),
        dbc.Card(dbc.CardBody([
            dbc.Row([
                dbc.Col(dbc.Input(id="sym", placeholder="Symbol", value="BTCUSDT"), md=3),
                dbc.Col(dcc.Slider(1, 30, 1, value=5, id="hz",
                                   marks=None, tooltip={"placement":"bottom","always_visible":True}), md=6),
                dbc.Col(dbc.Button("Run Forecast", id="go", color="primary"), md=3)
            ], align="center"),
            dbc.Row([
                dbc.Col(dcc.Checklist(options=[{"label":" Auto-refresh (15s)", "value":"on"}],
                                      value=[], id="auto"), md=4)
            ])
        ]), className="mb-3"),
        dcc.Interval(id="poll", interval=15_000, n_intervals=0),
        dbc.Row([
            dbc.Col(dcc.Graph(id="fig"), md=8),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.Div(id="kpi-regime", className="kpi"),
                html.Div(id="kpi-entropy", className="kpi"),
                html.Div(id="kpi-edge", className="kpi"),
                html.Div(id="kpi-sfh", className="kpi"),
                html.Hr(),
                html.Div(id="chips", className="chips"),
                html.Div(id="paywall", className="mt-2"),
                html.Div(id="share", className="mt-2"),
            ])), md=4),
        ])
    ], fluid=True)

# ---------- callbacks ----------
@callback(
    Output("fig", "figure"),
    Output("kpi-regime", "children"),
    Output("kpi-entropy", "children"),
    Output("kpi-edge", "children"),
    Output("kpi-sfh", "children"),
    Output("chips", "children"),
    Output("paywall", "children"),
    Output("share", "children"),
    Input("go", "n_clicks"),
    Input("poll", "n_intervals"),
    State("auto", "value"),
    State("sym", "value"),
    State("hz", "value"),
    State("jwt", "data"),
    prevent_initial_call=True
)
def run(n, _tick, auto, sym, hz, tok):
    # only poll when checkbox on
    if (not n and "on" not in (auto or [])) and _tick > 0:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    res = forecast(tok, "crypto", sym, int(hz))
    if "_error" in res and res["_error"] == 402:
        url = res["_json"].get("checkout_url") or billing_checkout(tok, "Crypto").get("url")
        return (go.Figure(), "", "", "", "", "",
                dbc.Alert(dbc.Button("Subscribe to Crypto", href=url, target="_blank", color="warning"),
                          color="dark"),
                "")

    if "_error" in res:
        return go.Figure(), "", "", "", "", "", dbc.Alert("Auth required", color="danger"), ""

    evt  = res.get("event", {})
    fc   = (evt.get("forecast") or {}).get("points") or []
    met  = evt.get("metrics") or {}
    if not fc:
        return go.Figure(), "", "", "", "", "", "", ""

    xs   = [pd.to_datetime(p["ts"]) for p in fc]
    yhat = [float(p["yhat"]) for p in fc]
    q10  = [float(p.get("q10", p["yhat"])) for p in fc]
    q90  = [float(p.get("q90", p["yhat"])) for p in fc]

    fig = go.Figure()
    fig.add_scatter(x=xs, y=q90, name="q90", mode="lines", line=dict(width=0.1), showlegend=False)
    fig.add_scatter(x=xs, y=q10, name="q10", mode="lines", fill="tonexty",
                    line=dict(width=0.1), fillcolor="rgba(124,92,255,0.20)", showlegend=False)
    fig.add_scatter(x=xs, y=yhat, name="Forecast", mode="lines", line=dict(dash="dash", width=2))
    fig.update_layout(margin=dict(l=30,r=10,t=10,b=30), hovermode="x unified")

    chips = []
    xp = explain(tok, "crypto", sym, int(hz)) or {}
    tags = (xp.get("tags") or []) + (xp.get("archetype_tags") or [])
    for t in tags[:8]:
        chips.append(dbc.Badge(t, className="me-1 mb-1", color="secondary"))

    # share link
    sh = share_create(tok, "crypto", sym, int(hz), ttl_hours=24) or {}
    share = dbc.Button("Share 24h link", href=sh.get("url"), target="_blank", color="secondary") if sh.get("url") else ""

    return (fig,
            f"Regime: {met.get('regime', '—')}",
            f"Entropy: {met.get('entropy', '—')}",
            f"Edge: {met.get('edge', '—')}",
            f"SFH: {met.get('sfh_days', '—')} d",
            chips, "", share)
