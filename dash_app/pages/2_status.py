from dash import register_page, html, dcc
import dash_bootstrap_components as dbc
from dash_app.lib.api import public_slo, public_accuracy
import pandas as pd

register_page(__name__, path="/status", name="Status")

def layout():
    slo = public_slo() or {}
    acc = public_accuracy() or {}
    df  = pd.DataFrame(acc.get("arenas", [])) if acc else pd.DataFrame()
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True) if not df.empty else "—"
    return dbc.Container([
        html.H4("📊 Status & Accuracy"),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("SLO"),
                html.Div(f"p95 latency: {slo.get('latency_p95_ms','—')} ms"),
                html.Div(f"uptime(30d): {slo.get('uptime_30d','—')}"),
            ])), md=4),
            dbc.Col(dbc.Card(dbc.CardBody([html.H6("Accuracy"), table])), md=8)
        ])
    ], fluid=True)
