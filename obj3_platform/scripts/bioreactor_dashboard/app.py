import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from datetime import datetime
import serial_reader, data_store

serial_reader.start_reader()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Bioreactor dashboard"),
    html.Div(id="sensor-cards"),

    dcc.Graph(id="temp-graph"),
    dcc.Graph(id="ph-graph"),
    dcc.Graph(id="pressure-graph"),
    dcc.Graph(id="co2-graph"),

    html.H3("Actuator controls"),
    html.Div([
        html.Label("Agitator speed"),
        dcc.Slider(0, 100, 1, value=60, id="motor-speed",
                marks={0: "0%", 50: "50%", 100: "100%"}),
        html.Button("Pump A ON",  id="pump-a-btn", n_clicks=0),
        html.Button("Pump B ON",  id="pump-b-btn", n_clicks=0),
        html.Button("Heater ON",  id="heater-btn", n_clicks=0),
    ]),

    dcc.Interval(id="interval", interval=1500),
])

def make_figure(timestamps, values, title, color, unit):
    fig = go.Figure(go.Scatter(
        x=timestamps, y=values,
        mode="lines",
        line=dict(color=color, width=2)
    ))
    fig.update_layout(
        title=title,
        height=220,
        margin=dict(l=50, r=20, t=40, b=40),
        xaxis=dict(title="Time", tickformat="%H:%M:%S"),
        yaxis=dict(title=unit),
    )
    return fig

@app.callback(
    Output("sensor-cards",  "children"),
    Output("temp-graph",    "figure"),
    Output("ph-graph",      "figure"),
    Output("pressure-graph","figure"),
    Output("co2-graph",     "figure"),
    Input("interval", "n_intervals"),
)
def update(_):
    hist = data_store.history()
    ts   = [datetime.fromtimestamp(r["ts"]) for r in hist]

    def vals(key): return [r.get(key) for r in hist]

    latest = data_store.latest()
    cards = html.Div([
        html.Div(f'Temp: {latest.get("temp", "--")} °C'),
        html.Div(f'pH: {latest.get("ph", "--")}'),
        html.Div(f'Pressure: {latest.get("pressure", "--")} bar'),
        html.Div(f'CO₂: {latest.get("co2", "--")} ppm'),
    ])

    return (
        cards,
        make_figure(ts, vals("temp"),     "Temperature", "#378ADD", "°C"),
        make_figure(ts, vals("ph"),       "pH",          "#7F77DD", "pH"),
        make_figure(ts, vals("pressure"), "Pressure",    "#D85A30", "bar"),
        make_figure(ts, vals("co2"),      "CO₂",         "#639922", "ppm"),
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050, use_reloader=False)