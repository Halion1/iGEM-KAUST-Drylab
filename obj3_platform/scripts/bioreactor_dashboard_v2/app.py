import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from datetime import datetime
import serial_reader, data_store

serial_reader.start_reader()

DARK_PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#888", size=11),
    margin=dict(l=40, r=16, t=28, b=28),
    height=120,
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
)

def sparkline(ts, values, title, color, y_range, range_label):
    fig = go.Figure(go.Scatter(
        x=ts, y=values, mode="lines",
        line=dict(color=color, width=1.5),
        fill="tozeroy",
        fillcolor=color.replace(")", ",0.08)").replace("rgb", "rgba"),
    ))
    fig.update_layout(
        **DARK_PLOT,
        yaxis=dict(showgrid=True, gridcolor="#2e2e2e", zeroline=False, range=y_range),
        annotations=[
            dict(text=f"<b>{title}</b>", x=0, y=1.15, xref="paper", yref="paper",
                showarrow=False, font=dict(color="#e0e0e0", size=13)),
            dict(text=range_label, x=1, y=1.15, xref="paper", yref="paper",
                showarrow=False, font=dict(color="#555", size=11)),
        ],
    )
    return fig
app = dash.Dash(__name__)

app.layout = html.Div(className="dashboard", children=[
    html.Div(className="top-bar", children=[
        html.H1("Bioreactor dashboard"),
        html.Div(className="live-badge", children=[
            html.Div(className="live-dot"),
            "Live · Arduino R4 WiFi"
        ]),
    ]),

    html.Div(className="section-label", children="Sensors"),
    html.Div(className="sensor-grid", id="sensor-cards"),

    html.Div(className="section-label", children="Trend (last 60 s)"),
    html.Div(className="chart-card", children=[
        dcc.Graph(id="temp-graph", config={"displayModeBar": False}),
    ]),
    html.Div(className="chart-card", children=[
        dcc.Graph(id="ph-graph", config={"displayModeBar": False}),
    ]),
    html.Div(className="chart-card", children=[
        dcc.Graph(id="pressure-graph", config={"displayModeBar": False}),
    ]),
    html.Div(className="chart-card", children=[
        dcc.Graph(id="co2-graph", config={"displayModeBar": False}),
    ]),

html.Div(className="section-label", children="Actuators"),
html.Div(className="actuator-grid", children=[
    html.Div(className="act-card", children=[
        html.Div([html.Div("Pump A", className="act-name"),
                html.Div(id="pump-a-sub", children="Running", className="act-sub")]),
        html.Button(className="toggle on", id="pump-a-btn", n_clicks=0),
    ]),
    html.Div(className="act-card", children=[
        html.Div([html.Div("Pump B", className="act-name"),
                html.Div(id="pump-b-sub", children="Idle", className="act-sub")]),
        html.Button(className="toggle off", id="pump-b-btn", n_clicks=0),
    ]),
    html.Div(className="act-card", children=[
        html.Div([html.Div("Heating pads", className="act-name"),
                html.Div(id="heater-sub", children="Running", className="act-sub")]),
        html.Button(className="toggle on", id="heater-btn", n_clicks=0),
    ]),
    html.Div(className="act-card",
            style={"flexDirection":"column","alignItems":"stretch","gap":"8px"}, children=[
        html.Div("Agitator speed", className="act-name"),
        html.Div(style={"display":"flex","alignItems":"center","gap":"8px"}, children=[
            dcc.Slider(0, 100, 1, value=60, id="motor-speed",
                    marks=None, tooltip={"always_visible": False}),
            html.Div("60%", id="motor-label",
                    style={"fontSize":"12px","color":"#888","minWidth":"30px"}),
        ]),
    ]),
]),

    html.Div(className="power-row", children=[
        html.Div([
            html.Div("Power station", className="power-label"),
            html.Div("211 Wh remaining", className="power-value"),
        ]),
        html.Div(className="power-track", children=[
            html.Div(style={"width": "72%", "height": "100%",
                            "background": "#1D9E75", "borderRadius": "3px"}),
        ]),
        html.Div("72%", className="power-pct"),
    ]),

    html.Div(className="section-label", children="Event log"),
    html.Div(className="log-card", id="event-log"),

    dcc.Interval(id="interval", interval=1500),
])

def sensor_card(label, value, unit, pct, color):
    return html.Div(className="sensor-card", children=[
        html.Div(label, className="s-label"),
        html.Div([value, html.Span(unit, className="s-unit")], className="s-value"),
        html.Div(className="bar-track", children=[
            html.Div(className="bar-fill",
                    style={"width": f"{pct}%", "background": color}),
        ]),
    ])

@app.callback(
    Output("sensor-cards",   "children"),
    Output("temp-graph",     "figure"),
    Output("ph-graph",       "figure"),
    Output("pressure-graph", "figure"),
    Output("co2-graph",      "figure"),
    Input("interval", "n_intervals"),
)
def update(_):
    try:
        hist = data_store.history()

        empty_fig = go.Figure()
        empty_fig.update_layout(**DARK_PLOT)
        if not hist:
            return [], empty_fig, empty_fig, empty_fig, empty_fig

        ts = [datetime.fromtimestamp(r["ts"]) for r in hist]
        def v(k): return [r.get(k) for r in hist]

        latest = data_store.latest()
        temp = latest.get("temp", 0)
        ph   = latest.get("ph",   0)
        pres = latest.get("pressure", 0)
        co2  = latest.get("co2",  0)

        cards = [
            sensor_card("Temperature", f"{temp:.1f}", "°C",  (temp-35)/5*100,    "#378ADD"),
            sensor_card("pH",          f"{ph:.2f}",   "pH",  (ph-6.5)/1.0*100,   "#7F77DD"),
            sensor_card("Pressure",    f"{pres:.3f}", "bar", (pres-0.9)/0.3*100, "#D85A30"),
            sensor_card("CO₂",         f"{co2:.0f}",  "ppm", co2/600*100,        "#639922"),
        ]

        return (
            cards,
            sparkline(ts, v("temp"),     "Temperature", "rgb(55,138,221)",  [35, 40],   "35 – 40 °C"),
            sparkline(ts, v("ph"),       "pH",          "rgb(127,119,221)", [6.5, 7.5], "6.5 – 7.5"),
            sparkline(ts, v("pressure"), "Pressure",    "rgb(216,90,48)",   [0.9, 1.2], "0.9 – 1.2 bar"),
            sparkline(ts, v("co2"),      "CO₂",         "rgb(99,153,34)",   [380, 450], "380 – 450 ppm"),
        )

    except Exception as e:
        import traceback
        traceback.print_exc()   # prints full error to your terminal
        raise

@app.callback(
    Output("motor-label", "children"),
    Input("motor-speed", "value"),
)
def motor_label(val):
    return f"{val}%"

@app.callback(
    Output("pump-a-btn", "className"), Output("pump-a-sub", "children"),
    Input("pump-a-btn", "n_clicks"), prevent_initial_call=True
)
def toggle_pump_a(n):
    return ("toggle on", "Running") if n % 2 == 0 else ("toggle off", "Idle")

@app.callback(
    Output("pump-b-btn", "className"), Output("pump-b-sub", "children"),
    Input("pump-b-btn", "n_clicks"), prevent_initial_call=True
)
def toggle_pump_b(n):
    return ("toggle on", "Running") if n % 2 == 1 else ("toggle off", "Idle")

@app.callback(
    Output("heater-btn", "className"), Output("heater-sub", "children"),
    Input("heater-btn", "n_clicks"), prevent_initial_call=True
)
def toggle_heater(n):
    return ("toggle on", "Running") if n % 2 == 0 else ("toggle off", "Idle")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050, use_reloader=False)