import colorsys
import math
from pathlib import Path

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, callback, ctx, dcc, html, no_update
from dash_iconify import DashIconify
from flask import Response

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
    return html.Div(id={"type": "picker-petal", "color": color}, n_clicks=0, style=style)


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
    return html.Div(id={"type": "picker-ring", "color": color}, n_clicks=0, style=style)


_SHAPES = ["Wheel", "Flower", "Ring"]
_HINTS = {
    "Wheel": "Click anywhere on the wheel to sample that exact color.",
    "Flower": "Click a petal to pick its color.",
    "Ring": "Click a circle on the ring to pick its color.",
}

NAME = "Color Picker *"
DESCRIPTION = "A color picker with three switchable shapes: a continuous HSV wheel, clickable petals, and a ring of swatches."
DOC_TEXT = (
    "A `dmc.SegmentedControl` filters which shape is visible. Wheel is a "
    "`dcc.Graph` showing a static HSV raster (hue by angle, saturation by "
    "radius); clicking it reads the exact pixel back off `clickData`. Flower "
    "and Ring are `html.Div`s carrying a pattern-matching id — "
    '`{"type": "picker-petal"/"picker-ring", "color": <hex>}` — so one '
    "callback can listen to all three shapes at once and tell them apart "
    "via `ctx.triggered_id`. All three stay mounted; only their `display` "
    "style toggles when you switch shapes."
)

LLMS_DOC = f"# {NAME}\n\n> {DESCRIPTION}\n\n{DOC_TEXT}\n"

_WHEEL_BOX_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": 12,
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
    "display": "inline-block",
}

_wheel_graph = dcc.Graph(
    id="picker-wheel",
    figure=_wheel_figure(),
    config={"displayModeBar": False, "scrollZoom": False},
    style={"width": _WHEEL_SIZE, "height": _WHEEL_SIZE, "cursor": "crosshair"},
    clear_on_unhover=True,
)
_wheel = html.Div(
    dmc.FloatingTooltip(
        html.Div(_wheel_graph, style=_WHEEL_BOX_STYLE),
        id="picker-wheel-tooltip",
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

_copy_button = dmc.Tooltip(
    dmc.Button(
        dmc.Group(
            [DashIconify(icon="mdi:file-document-outline", width=14), "Copy llms.txt URL"],
            gap=6,
            wrap="nowrap",
        ),
        id="llm-copy-button-color-picker",
        variant="subtle",
        color="gray",
        size="compact-sm",
        className="llms-copy-button",
    ),
    label="Copy this page's /llms.txt URL — paste into ChatGPT, Claude, or any LLM",
    position="top",
    withArrow=True,
)

_code_tabs = dmc.CodeHighlightTabs(
    code=[
        {
            "fileName": Path(__file__).name,
            "code": Path(__file__).read_text(encoding="utf-8"),
            "language": "python",
            "icon": DashIconify(icon="devicon:python"),
        }
    ],
    defaultExpanded=False,
    withExpandButton=True,
)

app = Dash(__name__)


@app.server.route("/llms.txt")
def llms_txt():
    return Response(LLMS_DOC, mimetype="text/plain")


app.layout = dmc.MantineProvider(
    dmc.Container(
        size="sm",
        py="xl",
        children=dmc.Stack(
            gap="lg",
            align="center",
            children=[
                dmc.Title(NAME, order=2),
                dmc.Text(DESCRIPTION, size="sm", c="dimmed", ta="center"),
                dmc.Box(_copy_button),
                dmc.SegmentedControl(id="picker-shape", data=_SHAPES, value="Wheel"),
                dmc.Text(id="picker-hint", size="sm", c="dimmed"),
                html.Div(_wheel, id="picker-shape-wheel"),
                html.Div(_flower, id="picker-shape-flower", style={"display": "none"}),
                html.Div(_ring, id="picker-shape-ring", style={"display": "none"}),
                dmc.Box(id="picker-center", style=_CENTER_BASE_STYLE),
                dmc.Code(id="picker-hex"),
                dmc.Divider(w="100%"),
                dmc.Stack(
                    gap="xs",
                    children=[
                        dmc.Title("How it works", order=4),
                        dmc.Text(DOC_TEXT, size="sm", mb="sm"),
                        _code_tabs,
                    ],
                ),
            ],
        ),
    )
)


@callback(
    Output("picker-shape-wheel", "style"),
    Output("picker-shape-flower", "style"),
    Output("picker-shape-ring", "style"),
    Output("picker-hint", "children"),
    Input("picker-shape", "value"),
)
def switch_shape(shape):
    styles = {name: {"display": "block" if name == shape else "none"} for name in _SHAPES}
    return styles["Wheel"], styles["Flower"], styles["Ring"], _HINTS.get(shape, "")


@callback(
    Output("picker-wheel-tooltip", "label"),
    Input("picker-wheel", "hoverData"),
)
def show_hover_hex(hover_data):
    if not hover_data:
        return _DEFAULT_COLOR
    point = hover_data["points"][0]
    return _hex_from_pixel(point["x"], point["y"])


@callback(
    Output("picker-center", "style"),
    Output("picker-hex", "children"),
    Output("picker-wheel", "figure"),
    Input("picker-wheel", "clickData"),
    Input({"type": "picker-petal", "color": ALL}, "n_clicks"),
    Input({"type": "picker-ring", "color": ALL}, "n_clicks"),
)
def pick_color(click_data, _petal_clicks, _ring_clicks):
    triggered = ctx.triggered_id
    figure = no_update
    if triggered == "picker-wheel" and click_data:
        point = click_data["points"][0]
        x, y = point["x"], point["y"]
        hex_color = _hex_from_pixel(x, y)
        figure = _wheel_figure((x, y))
    elif isinstance(triggered, dict) and triggered.get("type") in ("picker-petal", "picker-ring"):
        hex_color = triggered["color"]
    else:
        hex_color = _DEFAULT_COLOR
    style = {**_CENTER_BASE_STYLE, "backgroundColor": hex_color}
    return style, hex_color, figure


if __name__ == "__main__":
    app.run(debug=True, port=8560)
