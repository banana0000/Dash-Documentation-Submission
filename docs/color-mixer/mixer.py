import colorsys
import math

from dash import ALL, Input, Output, callback, ctx, dcc, html, no_update
import dash_mantine_components as dmc
import plotly.graph_objects as go

_DEFAULT_COLOR = "#f03e3e"

_CENTER_SIZE = 70
_CENTER_BASE_STYLE = {
    "width": _CENTER_SIZE,
    "height": _CENTER_SIZE,
    "borderRadius": "50%",
    "border": "3px solid var(--mantine-color-body)",
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.3)",
    "transition": "background-color 120ms ease",
}

_WHEEL_SIZE = 220


def _hue_sat_from_pixel(x, y, size=_WHEEL_SIZE):
    center = (size - 1) / 2
    radius = size / 2
    dx = x - center
    dy = center - y
    r = math.hypot(dx, dy) / radius
    theta = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    return theta / 360, min(r, 1.0)


def _build_wheel_rgba(size=_WHEEL_SIZE):
    rgba = [[(0, 0, 0, 0)] * size for _ in range(size)]
    radius = size / 2
    center = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            if math.hypot(x - center, center - y) > radius:
                continue
            hue, sat = _hue_sat_from_pixel(x, y, size)
            r, g, b = colorsys.hsv_to_rgb(hue, sat, 1.0)
            rgba[y][x] = (round(r * 255), round(g * 255), round(b * 255), 255)
    return rgba


def _hex_from_pixel(x, y, size=_WHEEL_SIZE):
    hue, sat = _hue_sat_from_pixel(x, y, size)
    r, g, b = colorsys.hsv_to_rgb(hue, sat, 1.0)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


_WHEEL_RGBA = _build_wheel_rgba()


def _wheel_figure(marker_xy=None):
    fig = go.Figure(go.Image(z=_WHEEL_RGBA, hoverinfo="skip"))
    if marker_xy is not None:
        mx, my = marker_xy
        fig.add_trace(
            go.Scatter(
                x=[mx],
                y=[my],
                mode="markers",
                marker=dict(size=16, color="rgba(0, 0, 0, 0)", line=dict(width=3, color="white")),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.update_xaxes(visible=False, showgrid=False, range=[0, _WHEEL_SIZE])
    fig.update_yaxes(visible=False, showgrid=False, range=[_WHEEL_SIZE, 0])
    fig.update_layout(
        width=_WHEEL_SIZE,
        height=_WHEEL_SIZE,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        dragmode=False,
        hovermode="closest",
    )
    return fig


_PETAL_COLORS = ["#f03e3e", "#fab005", "#40c057", "#228be6", "#7950f2", "#e64980"]
_PETAL_WIDTH = 52
_PETAL_HEIGHT = 92
_FLOWER_SIZE = 200

_PETAL_BASE_STYLE = {
    "position": "absolute",
    "width": _PETAL_WIDTH,
    "height": _PETAL_HEIGHT,
    "borderRadius": "50%",
    "top": "50%",
    "left": "50%",
    "marginTop": -_PETAL_HEIGHT,
    "marginLeft": -_PETAL_WIDTH // 2,
    "transformOrigin": "50% 100%",
    "cursor": "pointer",
    "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.25)",
    "border": "2px solid rgba(255, 255, 255, 0.6)",
}


def _petal(color, angle):
    style = {**_PETAL_BASE_STYLE, "backgroundColor": color, "transform": f"rotate({angle}deg)"}
    return html.Div(id={"type": "mixer-demo-petal", "color": color}, n_clicks=0, style=style)


_RING_COUNT = 12
_RING_SIZE = 220
_RING_RADIUS = 90
_SWATCH_SIZE = 34


def _ring_colors(count=_RING_COUNT):
    return [
        "#{:02x}{:02x}{:02x}".format(*(round(c * 255) for c in colorsys.hsv_to_rgb(i / count, 1.0, 1.0)))
        for i in range(count)
    ]


def _ring_swatch(color, angle_deg):
    angle = math.radians(angle_deg)
    cx = cy = _RING_SIZE / 2
    x = cx + _RING_RADIUS * math.sin(angle) - _SWATCH_SIZE / 2
    y = cy - _RING_RADIUS * math.cos(angle) - _SWATCH_SIZE / 2
    style = {
        "position": "absolute",
        "left": x,
        "top": y,
        "width": _SWATCH_SIZE,
        "height": _SWATCH_SIZE,
        "borderRadius": "50%",
        "backgroundColor": color,
        "cursor": "pointer",
        "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.25)",
        "border": "2px solid rgba(255, 255, 255, 0.6)",
    }
    return html.Div(id={"type": "mixer-demo-ring", "color": color}, n_clicks=0, style=style)


_SHAPES = ["Wheel", "Flower", "Ring"]
_HINTS = {
    "Wheel": "Click anywhere on the wheel to sample that exact color.",
    "Flower": "Click a petal to pick its color.",
    "Ring": "Click a circle on the ring to pick its color.",
}

_WHEEL_BOX_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": 12,
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
    "display": "inline-block",
}

_wheel_graph = dcc.Graph(
    id="mixer-demo-wheel",
    figure=_wheel_figure(),
    config={"displayModeBar": False, "scrollZoom": False},
    style={"width": _WHEEL_SIZE, "height": _WHEEL_SIZE, "cursor": "crosshair"},
    clear_on_unhover=True,
)
_wheel = html.Div(
    dmc.FloatingTooltip(
        html.Div(_wheel_graph, style=_WHEEL_BOX_STYLE),
        id="mixer-demo-wheel-tooltip",
        label=_DEFAULT_COLOR,
        color="dark",
    )
)
_flower = html.Div(
    [_petal(c, i * 360 / len(_PETAL_COLORS)) for i, c in enumerate(_PETAL_COLORS)],
    style={"position": "relative", "width": _FLOWER_SIZE, "height": _FLOWER_SIZE},
)
_ring = html.Div(
    [_ring_swatch(c, i * 360 / len(_ring_colors())) for i, c in enumerate(_ring_colors())],
    style={"position": "relative", "width": _RING_SIZE, "height": _RING_SIZE},
)

component = dmc.Stack(
    gap="lg",
    align="center",
    children=[
        dmc.SegmentedControl(id="mixer-demo-shape", data=_SHAPES, value="Wheel"),
        dmc.Text(id="mixer-demo-hint", size="sm", c="dimmed"),
        html.Div(_wheel, id="mixer-demo-shape-wheel"),
        html.Div(_flower, id="mixer-demo-shape-flower", style={"display": "none"}),
        html.Div(_ring, id="mixer-demo-shape-ring", style={"display": "none"}),
        dmc.Box(id="mixer-demo-center", style=_CENTER_BASE_STYLE),
        dmc.Code(id="mixer-demo-hex"),
    ],
)


@callback(
    Output("mixer-demo-shape-wheel", "style"),
    Output("mixer-demo-shape-flower", "style"),
    Output("mixer-demo-shape-ring", "style"),
    Output("mixer-demo-hint", "children"),
    Input("mixer-demo-shape", "value"),
)
def switch_shape(shape):
    styles = {name: {"display": "block" if name == shape else "none"} for name in _SHAPES}
    return styles["Wheel"], styles["Flower"], styles["Ring"], _HINTS.get(shape, "")


@callback(
    Output("mixer-demo-wheel-tooltip", "label"),
    Input("mixer-demo-wheel", "hoverData"),
)
def show_hover_hex(hover_data):
    if not hover_data:
        return _DEFAULT_COLOR
    point = hover_data["points"][0]
    return _hex_from_pixel(point["x"], point["y"])


@callback(
    Output("mixer-demo-center", "style"),
    Output("mixer-demo-hex", "children"),
    Output("mixer-demo-wheel", "figure"),
    Input("mixer-demo-wheel", "clickData"),
    Input({"type": "mixer-demo-petal", "color": ALL}, "n_clicks"),
    Input({"type": "mixer-demo-ring", "color": ALL}, "n_clicks"),
)
def pick_color(click_data, _petal_clicks, _ring_clicks):
    triggered = ctx.triggered_id
    figure = no_update
    if triggered == "mixer-demo-wheel" and click_data:
        point = click_data["points"][0]
        x, y = point["x"], point["y"]
        hex_color = _hex_from_pixel(x, y)
        figure = _wheel_figure((x, y))
    elif isinstance(triggered, dict) and triggered.get("type") in ("mixer-demo-petal", "mixer-demo-ring"):
        hex_color = triggered["color"]
    else:
        hex_color = _DEFAULT_COLOR
    style = {**_CENTER_BASE_STYLE, "backgroundColor": hex_color}
    return style, hex_color, figure
