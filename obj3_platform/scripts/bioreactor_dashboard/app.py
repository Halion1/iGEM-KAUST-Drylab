import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import serial_reader, data_store

serial_reader.start_reader()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Bioreactor dashboard"),
    html.Div(id="sensor-cards"),

    dcc.Graph(id="temp-graph"),
    dcc.Graph(id="ph-graph"),
    dcc.Graph(id="co2-graph"),
    dcc.Graph(id="pressure-graph"),

    html.H3("Actuator controls"),
    html.Div([
        html.Label("Agitator speed"),
        dcc.Slider(0, 100, 1, value=60, id="motor-speed",
                marks={0:"0%", 50:"50%", 100:"100%"}),
        html.Button("Pump A ON",  id="pump-a-btn", n_clicks=0),
        html.Button("Pump B ON",  id="pump-b-btn", n_clicks=0),
        html.Button("Heater ON",  id="heater-btn", n_clicks=0),
    ]),

    dcc.Interval(id="interval", interval=1500),   # refresh every 1.5 s
])

@app.callback(
    Output("sensor-cards", "children"),
    Output("temp-graph",   "figure"),
    Output("ph-graph",     "figure"),
    Input("interval", "n_intervals"),
)
def update(n):
    hist = data_store.history()
    ts   = [r["ts"]       for r in hist]
    temp = [r.get("temp") for r in hist]
    ph   = [r.get("ph")   for r in hist]

    latest = data_store.latest()

    cards = html.Div([
        html.Div(f'Temp: {latest.get("temp","--")} °C'),
        html.Div(f'pH: {latest.get("ph","--")}'),
        html.Div(f'Pressure: {latest.get("pressure","--")} bar'),
        html.Div(f'CO₂: {latest.get("co2","--")} ppm'),
    ])

    def sparkline(x, y, title, color):
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines",
                                line=dict(color=color, width=2)))
        fig.update_layout(title=title, height=200, margin=dict(l=40,r=20,t=30,b=20))
        return fig

    return (
        cards,
        sparkline(ts, temp, "Temperature (°C)", "#378ADD"),
        sparkline(ts, ph,   "pH",               "#7F77DD"),
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)