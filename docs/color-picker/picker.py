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
    # Opaque white, not transparent black: go.Image doesn't composite alpha=0
    # against paper_bgcolor, so a "transparent" corner rendered as solid
    # black instead of blending into the white card underneath.
    rgba = [[(255, 255, 255, 255)] * size for _ in range(size)]
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


# ---------------------------------------------------------------------------
# Shape 4: Photo — a generated, photo-like raster (no formula recovers a
# color from its position, unlike the wheel, so hover and click both read an
# actual pixel table instead of computing hue/saturation).
# ---------------------------------------------------------------------------

_PHOTO_SIZE = 180


def _build_photo_rgba(size=_PHOTO_SIZE):
    """A warm-to-cool gradient with a soft glow, computed once at import —
    same `colorsys` toolkit as the wheel, just without the wheel's polar
    symmetry, so it reads as a photo rather than a control."""
    rgba = [[(0, 0, 0, 255)] * size for _ in range(size)]
    glow_x, glow_y = size * 0.68, size * 0.32
    for y in range(size):
        t = y / (size - 1)
        hue = (0.06 + 0.55 * t) % 1.0
        sat = 0.5 + 0.35 * math.sin(t * math.pi)
        base_val = 1.0 - 0.3 * t
        for x in range(size):
            dx = (x - glow_x) / size
            dy = (y - glow_y) / size
            glow = max(0.0, 1.0 - 5.5 * math.hypot(dx, dy))
            h = (hue + 0.04 * math.sin(x / size * math.pi * 2)) % 1.0
            v = min(1.0, base_val + glow * 0.45)
            r, g, b = colorsys.hsv_to_rgb(h, sat, v)
            rgba[y][x] = (round(r * 255), round(g * 255), round(b * 255), 255)
    return rgba


_PHOTO_RGBA = _build_photo_rgba()
_PHOTO_HEX = [
    ["#{:02x}{:02x}{:02x}".format(*pixel[:3]) for pixel in row]
    for row in _PHOTO_RGBA
]


def _hex_from_photo_pixel(x, y, size=_PHOTO_SIZE):
    xi = min(max(round(x), 0), size - 1)
    yi = min(max(round(y), 0), size - 1)
    return _PHOTO_HEX[yi][xi]


def _photo_figure():
    """`customdata` ships the real per-pixel hex to the browser — there's no
    cheap formula to recompute it from (x, y) the way the wheel's hover does,
    so the hover callback below reads this instead of doing HSV math in JS."""
    fig = go.Figure(
        go.Image(
            z=_PHOTO_RGBA,
            customdata=_PHOTO_HEX,
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
    fig.update_xaxes(visible=False, showgrid=False, range=[0, _PHOTO_SIZE])
    fig.update_yaxes(visible=False, showgrid=False, range=[_PHOTO_SIZE, 0])
    fig.update_layout(
        width=_PHOTO_SIZE,
        height=_PHOTO_SIZE,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        dragmode=False,
        hovermode="closest",
    )
    return fig


_PETAL_OUTER_COLORS = ["#f03e3e", "#fab005", "#40c057", "#228be6", "#7950f2", "#e64980"]
_PETAL_OUTER_WIDTH = 52
_PETAL_OUTER_HEIGHT = 92
_PETAL_INNER_WIDTH = 34
_PETAL_INNER_HEIGHT = 58
_FLOWER_SIZE = 200


def _tint(hex_color, saturation_scale=0.45):
    """A lighter version of `hex_color`, same hue, so the inner layer reads
    as "the same flower, closer to the center" rather than a clashing set."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, _v = colorsys.rgb_to_hsv(r, g, b)
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s * saturation_scale, 1.0)
    return "#{:02x}{:02x}{:02x}".format(round(r2 * 255), round(g2 * 255), round(b2 * 255))


# Offset by half a step from the outer ring so the two layers interleave
# instead of one hiding directly behind the other.
_PETAL_INNER_COLORS = [_tint(c) for c in _PETAL_OUTER_COLORS]
_PETAL_INNER_OFFSET = 180 / len(_PETAL_OUTER_COLORS)


def _petal_style(width, height):
    return {
        "position": "absolute",
        "width": width,
        "height": height,
        "borderRadius": "50%",
        "top": "50%",
        "left": "50%",
        "marginTop": -height,
        "marginLeft": -width // 2,
        "transformOrigin": "50% 100%",
        "cursor": "pointer",
        "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.25)",
        "border": "2px solid rgba(255, 255, 255, 0.6)",
    }


def _petal(color, angle, width=_PETAL_OUTER_WIDTH, height=_PETAL_OUTER_HEIGHT):
    style = {**_petal_style(width, height), "backgroundColor": color, "transform": f"rotate({angle}deg)"}
    return html.Div(
        id={"type": "picker-demo-petal", "color": color},
        n_clicks=0,
        style=style,
        **{"data-picker-color": color},
    )


def _petal_layer(colors, width, height, offset=0):
    """One ring of petals, evenly spaced starting at `offset` degrees."""
    return [_petal(c, offset + i * 360 / len(colors), width, height) for i, c in enumerate(colors)]


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


_SHAPES = ["Wheel", "Flower", "Ring", "Photo"]
_HINTS = {
    "Wheel": "Hover to preview, click to lock that exact color.",
    "Flower": "Hover a petal to preview, click to lock it.",
    "Ring": "Hover a circle to preview, click to lock it.",
    "Photo": "Hover the image to preview, click to lock that exact pixel's color.",
}

_WHEEL_BOX_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": 12,
    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
    "display": "inline-block",
}

# No card, no background — the square figure is clipped to a circle by CSS,
# so the corners (whatever color they are) are never drawn at all instead of
# relying on go.Image to composite alpha=0 against paper_bgcolor, which it
# doesn't: those pixels rendered opaque black regardless of alpha.
_WHEEL_WRAP_STYLE = {
    "borderRadius": "50%",
    "overflow": "hidden",
    "display": "inline-block",
    "lineHeight": 0,
}

_wheel_graph = dcc.Graph(
    id="picker-demo-wheel",
    figure=_wheel_figure(),
    config={"displayModeBar": False, "scrollZoom": False},
    # without this, hoverData keeps its last value on mouse-out and the preview sticks
    clear_on_unhover=True,
    # "pointer", not "crosshair" — matches the petals and ring so all three
    # shapes signal "clickable" the same way.
    style={"width": _WHEEL_SIZE, "height": _WHEEL_SIZE, "cursor": "pointer"},
)
_wheel = html.Div(_wheel_graph, style=_WHEEL_WRAP_STYLE)
_photo_graph = dcc.Graph(
    id="picker-demo-photo",
    figure=_photo_figure(),
    config={"displayModeBar": False, "scrollZoom": False},
    clear_on_unhover=True,
    style={"width": _PHOTO_SIZE, "height": _PHOTO_SIZE, "cursor": "pointer"},
)
_photo = html.Div(_photo_graph, style=_WHEEL_BOX_STYLE)
_flower = html.Div(
    # Outer layer first (painted underneath), inner layer on top so the
    # shorter petals aren't hidden behind the taller ones.
    _petal_layer(_PETAL_OUTER_COLORS, _PETAL_OUTER_WIDTH, _PETAL_OUTER_HEIGHT)
    + _petal_layer(_PETAL_INNER_COLORS, _PETAL_INNER_WIDTH, _PETAL_INNER_HEIGHT, offset=_PETAL_INNER_OFFSET),
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
        html.Div(_photo, id="picker-demo-shape-photo", style={"display": "none"}),
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
    Output("picker-demo-shape-photo", "style"),
    Output("picker-demo-hint", "children"),
    Input("picker-demo-shape", "value"),
)
def switch_shape(shape):
    styles = {name: {"display": "block" if name == shape else "none"} for name in _SHAPES}
    return styles["Wheel"], styles["Flower"], styles["Ring"], styles["Photo"], _HINTS.get(shape, "")


@callback(
    Output("picker-demo-center", "style"),
    Output("picker-demo-hex", "children"),
    Output("picker-demo-wheel", "figure"),
    Output("picker-demo-photo", "figure"),
    Input("picker-demo-wheel", "clickData"),
    Input("picker-demo-photo", "clickData"),
    Input({"type": "picker-demo-petal", "color": ALL}, "n_clicks"),
    Input({"type": "picker-demo-ring", "color": ALL}, "n_clicks"),
)
def pick_color(wheel_click, photo_click, _petal_clicks, _ring_clicks):
    """Locks the selection. Python stays the source of truth for the final hex."""
    triggered = ctx.triggered_id
    wheel_figure = no_update
    photo_figure = no_update
    if triggered == "picker-demo-wheel" and wheel_click:
        point = wheel_click["points"][0]
        x, y = point["x"], point["y"]
        hex_color = _hex_from_pixel(x, y)
        # Patch sends ~40 bytes instead of re-serializing the whole raster
        wheel_figure = Patch()
        wheel_figure["data"][1]["x"] = [x]
        wheel_figure["data"][1]["y"] = [y]
    elif triggered == "picker-demo-photo" and photo_click:
        point = photo_click["points"][0]
        x, y = point["x"], point["y"]
        hex_color = _hex_from_photo_pixel(x, y)
        photo_figure = Patch()
        photo_figure["data"][1]["x"] = [x]
        photo_figure["data"][1]["y"] = [y]
    elif isinstance(triggered, dict) and triggered.get("type") in (
        "picker-demo-petal",
        "picker-demo-ring",
    ):
        hex_color = triggered["color"]
    else:
        hex_color = _DEFAULT_COLOR
    style = {**_CENTER_BASE_STYLE, "backgroundColor": hex_color}
    return style, hex_color, wheel_figure, photo_figure


# --- hover preview: wheel + photo -----------------------------------------
# Runs entirely in the browser. hoverData fires on every pixel move, so a
# server round trip here would be unusable. Two Inputs, one callback — a
# second callback targeting the same two Outputs would need
# allow_duplicate=True on every branch but one, which is more machinery than
# just checking which graph actually triggered.
clientside_callback(
    """
    function(wheelHover, photoHover) {
        const base = __PREVIEW_STYLE__;
        const empty = [Object.assign({}, base, {opacity: 0}), ""];
        const triggered = window.dash_clientside.callback_context.triggered_id;

        if (triggered === "picker-demo-wheel") {
            if (!wheelHover || !wheelHover.points || !wheelHover.points.length) {
                return empty;
            }
            // The wheel has no per-pixel table — hue/saturation come back
            // from the same polar math _hue_sat_from_pixel runs in Python.
            const SIZE = __WHEEL_SIZE__;
            const p = wheelHover.points[0];
            const c = (SIZE - 1) / 2;
            const radius = SIZE / 2;
            const dx = p.x - c;
            const dy = c - p.y;
            const sat = Math.min(Math.hypot(dx, dy) / radius, 1);
            const hue = ((Math.atan2(dy, dx) * 180 / Math.PI) + 360) % 360;
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

        if (triggered === "picker-demo-photo") {
            if (!photoHover || !photoHover.points || !photoHover.points.length) {
                return empty;
            }
            // The photo is an arbitrary raster — no formula recovers its
            // color from (x, y), so `customdata` carries the real per-pixel
            // hex straight from Python instead.
            const hex = photoHover.points[0].customdata;
            return [
                Object.assign({}, base, {opacity: __PREVIEW_OPACITY__, backgroundColor: hex}),
                hex
            ];
        }

        return window.dash_clientside.no_update;
    }
    """.replace("__PREVIEW_STYLE__", _PREVIEW_STYLE_JS)
    .replace("__WHEEL_SIZE__", str(_WHEEL_SIZE))
    .replace("__PREVIEW_OPACITY__", str(_PREVIEW_OPACITY)),
    Output("picker-demo-preview", "style"),
    Output("picker-demo-hover-hex", "children"),
    Input("picker-demo-wheel", "hoverData"),
    Input("picker-demo-photo", "hoverData"),
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
