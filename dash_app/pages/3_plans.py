from dash import register_page, html
import dash_bootstrap_components as dbc
from dash_app.lib.api import public_plans
import pandas as pd

register_page(__name__, path="/plans", name="Plans")

def layout():
    plans = public_plans() or {}
    df = pd.DataFrame(plans.get("plans", []))
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True) if not df.empty else "—"
    return dbc.Container([html.H4("🧾 Plans"), table], fluid=True)
