import colorsys
import json
import math

from dash import (
    ALL,
    Input,
    Output,
    Patch,
    callback,
    clientside_callback,
    ctx,
    dcc,
    html,
    no_update,
)
import dash_mantine_components as dmc
import plotly.graph_objects as go

_DEFAULT_COLOR = "#f03e3e"

_CENTER_SIZE = 70
_CENTER_BASE_STYLE = {
    # position:relative anchors the hover-preview overlay
    "position": "relative",
    "width": _CENTER_SIZE,
    "height": _CENTER_SIZE,
    "borderRadius": "50%",
    "border": "3px solid var(--mantine-color-body)",
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.3)",
    "transition": "background-color 120ms ease",
}

# The preview overlay sits on top of the locked color. Two separate elements means
# hover (clientside) and click (server) never fight over the same Output.
_PREVIEW_BASE_STYLE = {
    "position": "absolute",
    "inset": 0,
    "borderRadius": "50%",
    "opacity": 0,
    "pointerEvents": "none",
    "transition": "opacity 90ms ease, background-color 90ms ease",
}
_PREVIEW_OPACITY = 0.55
_PREVIEW_STYLE_JS = json.dumps(_PREVIEW_BASE_STYLE)

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


def _wheel_figure():
    """Built once, at import. The marker trace ships empty and is moved by Patch()."""
    fig = go.Figure(
        go.Image(
            z=_WHEEL_RGBA,
            # "none" hides the tooltip but still emits plotly_hover -> hoverData.
            # "skip" would kill the event entirely.
            hoverinfo="none",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[],
            y=[],
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
    return html.Div(
        id={"type": "picker-demo-petal", "color": color},
        n_clicks=0,
        style=style,
        **{"data-picker-color": color},
    )


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
    return html.Div(
        id={"type": "picker-demo-ring", "color": color},
        n_clicks=0,
        style=style,
        **{"data-picker-color": color},
    )


_SHAPES = ["Wheel", "Flower", "Ring"]
_HINTS = {
    "Wheel": "Hover to preview, click to lock that exact color.",
    "Flower": "Hover a petal to preview, click to lock it.",
    "Ring": "Hover a circle to preview, click to lock it.",
}

_WHEEL_BOX_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": 12,
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
    "display": "inline-block",
}

_wheel_graph = dcc.Graph(
    id="picker-demo-wheel",
    figure=_wheel_figure(),
    config={"displayModeBar": False, "scrollZoom": False},
    # without this, hoverData keeps its last value on mouse-out and the preview sticks
    clear_on_unhover=True,
    style={"width": _WHEEL_SIZE, "height": _WHEEL_SIZE, "cursor": "crosshair"},
)
_wheel = html.Div(_wheel_graph, style=_WHEEL_BOX_STYLE)
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
        dmc.SegmentedControl(id="picker-demo-shape", data=_SHAPES, value="Wheel"),
        dmc.Text(id="picker-demo-hint", size="sm", c="dimmed"),
        html.Div(_wheel, id="picker-demo-shape-wheel"),
        html.Div(_flower, id="picker-demo-shape-flower", style={"display": "none"}),
        html.Div(_ring, id="picker-demo-shape-ring", style={"display": "none"}),
        dmc.Box(
            id="picker-demo-center",
            style=_CENTER_BASE_STYLE,
            children=html.Div(id="picker-demo-preview", style=_PREVIEW_BASE_STYLE),
        ),
        dmc.Group(
            gap="xs",
            children=[
                dmc.Code(id="picker-demo-hex"),
                dmc.Text(id="picker-demo-hover-hex", size="xs", c="dimmed", ff="monospace"),
            ],
        ),
        # sink for the hover-listener installer below
        html.Div(id="picker-demo-bind-sink", style={"display": "none"}),
    ],
)


@callback(
    Output("picker-demo-shape-wheel", "style"),
    Output("picker-demo-shape-flower", "style"),
    Output("picker-demo-shape-ring", "style"),
    Output("picker-demo-hint", "children"),
    Input("picker-demo-shape", "value"),
)
def switch_shape(shape):
    styles = {name: {"display": "block" if name == shape else "none"} for name in _SHAPES}
    return styles["Wheel"], styles["Flower"], styles["Ring"], _HINTS.get(shape, "")


@callback(
    Output("picker-demo-center", "style"),
    Output("picker-demo-hex", "children"),
    Output("picker-demo-wheel", "figure"),
    Input("picker-demo-wheel", "clickData"),
    Input({"type": "picker-demo-petal", "color": ALL}, "n_clicks"),
    Input({"type": "picker-demo-ring", "color": ALL}, "n_clicks"),
)
def pick_color(click_data, _petal_clicks, _ring_clicks):
    """Locks the selection. Python stays the source of truth for the final hex."""
    triggered = ctx.triggered_id
    figure = no_update
    if triggered == "picker-demo-wheel" and click_data:
        point = click_data["points"][0]
        x, y = point["x"], point["y"]
        hex_color = _hex_from_pixel(x, y)
        # Patch sends ~40 bytes instead of re-serializing the whole raster
        figure = Patch()
        figure["data"][1]["x"] = [x]
        figure["data"][1]["y"] = [y]
    elif isinstance(triggered, dict) and triggered.get("type") in (
        "picker-demo-petal",
        "picker-demo-ring",
    ):
        hex_color = triggered["color"]
    else:
        hex_color = _DEFAULT_COLOR
    style = {**_CENTER_BASE_STYLE, "backgroundColor": hex_color}
    return style, hex_color, figure


# --- hover preview: wheel -------------------------------------------------
# Runs entirely in the browser. hoverData fires on every pixel move, so a
# server round trip here would be unusable.
clientside_callback(
    """
    function(hoverData) {
        const SIZE = __WHEEL_SIZE__;
        const base = __PREVIEW_STYLE__;
        if (!hoverData || !hoverData.points || !hoverData.points.length) {
            return [Object.assign({}, base, {opacity: 0}), ""];
        }
        const p = hoverData.points[0];
        const c = (SIZE - 1) / 2;
        const radius = SIZE / 2;
        const dx = p.x - c;
        const dy = c - p.y;
        const sat = Math.min(Math.hypot(dx, dy) / radius, 1);
        const hue = ((Math.atan2(dy, dx) * 180 / Math.PI) + 360) % 360;
        // HSV -> RGB with V = 1
        const chan = function (n) {
            const k = (n + hue / 60) % 6;
            return Math.round(255 * (1 - sat * Math.max(0, Math.min(k, 4 - k, 1))));
        };
        const hex = "#" + [chan(5), chan(3), chan(1)]
            .map(function (v) { return v.toString(16).padStart(2, "0"); })
            .join("");
        return [
            Object.assign({}, base, {opacity: __PREVIEW_OPACITY__, backgroundColor: hex}),
            hex
        ];
    }
    """.replace("__PREVIEW_STYLE__", _PREVIEW_STYLE_JS)
    .replace("__WHEEL_SIZE__", str(_WHEEL_SIZE))
    .replace("__PREVIEW_OPACITY__", str(_PREVIEW_OPACITY)),
    Output("picker-demo-preview", "style"),
    Output("picker-demo-hover-hex", "children"),
    Input("picker-demo-wheel", "hoverData"),
)

# --- hover preview: flower + ring ----------------------------------------
# html.Div has no hover prop, so bind native listeners once and push straight
# into the same two props with set_props (Dash >= 2.17).
clientside_callback(
    """
    function(_shape) {
        const base = __PREVIEW_STYLE__;
        const setPreview = function (hex) {
            window.dash_clientside.set_props("picker-demo-preview", {
                style: hex
                    ? Object.assign({}, base, {opacity: __PREVIEW_OPACITY__, backgroundColor: hex})
                    : Object.assign({}, base, {opacity: 0})
            });
            window.dash_clientside.set_props("picker-demo-hover-hex", {children: hex || ""});
        };
        document.querySelectorAll("[data-picker-color]").forEach(function (el) {
            if (el.dataset.pickerBound) { return; }
            el.dataset.pickerBound = "1";
            const hex = el.getAttribute("data-picker-color");
            el.addEventListener("mouseenter", function () { setPreview(hex); });
            el.addEventListener("mouseleave", function () { setPreview(null); });
        });
        return window.dash_clientside.no_update;
    }
    """.replace("__PREVIEW_STYLE__", _PREVIEW_STYLE_JS)
    .replace("__PREVIEW_OPACITY__", str(_PREVIEW_OPACITY)),
    Output("picker-demo-bind-sink", "children"),
    Input("picker-demo-shape", "value"),
)
