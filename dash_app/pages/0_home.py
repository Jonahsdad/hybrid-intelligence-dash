from dash import register_page, html, dcc
import dash_bootstrap_components as dbc

register_page(__name__, path="/")

layout = dbc.Container(
    [
        html.Div(className="hero", children=[
            html.H2("HYBRID INTELLIGENCE SYSTEMS"),
            html.Div("All arenas. Hybrid live. Powered by LIPE.", className="muted")
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("🔥 Crypto"),
                dbc.CardBody([
                    html.P("Bands • Regime • Entropy • Strategy", className="muted"),
                    dbc.Button("Enter", href="/crypto")
                ])
            ]), md=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("📊 Status"),
                dbc.CardBody([
                    html.P("Latency • Uptime • Accuracy", className="muted"),
                    dbc.Button("Open", href="/status")
                ])
            ]), md=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("🧾 Plans"),
                dbc.CardBody([
                    html.P("Pricing • Trials • Entitlements", className="muted"),
                    dbc.Button("View", href="/plans")
                ])
            ]), md=4),
        ], className="g-3"),
    ], fluid=True
)
