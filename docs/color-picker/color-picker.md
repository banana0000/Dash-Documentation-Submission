---
name: Color Picker *
description: A color picker with four switchable shapes -- a continuous HSV wheel, clickable petals, a ring of swatches, and a photo you sample like an eyedropper
endpoint: /examples/color-picker
package: color-picker
icon: mdi:palette-outline
---

.. llms_copy::Color Picker *

.. toc::

### Introduction

One color picker, four shapes. A `dmc.SegmentedControl` filters which shape
is visible — **Wheel** (a continuous HSV wheel), **Flower** (two layered
rings of six petals each — a lighter tint of the same hue nested inside the
full-saturation outer ring), **Ring** (twelve preset swatches arranged in a
circle), or **Photo** (a generated, photo-like image you sample pixel by
pixel). All four feed the same center swatch and hex readout: hover any of
them to preview a color, click to lock it in, like an eyedropper.

---

### Live Demo

Switch shapes with the control at the top; hover to preview, click to lock a color:

.. exec::docs.color-picker.picker
    :code: false
Source code:

.. source::docs/color-picker/picker.py

---

### How It Works

Every shape separates **preview** (hover, runs entirely client-side) from
**lock-in** (click, resolved server-side) into two different outputs, so the
two never fight over the same prop.

**Wheel** is a `dcc.Graph` showing a static HSV raster (hue by angle,
saturation by radius, value fixed at 1) built once at import time with
`colorsys.hsv_to_rgb`, sitting on an explicit white card (`backgroundColor:
"white"`) so it reads the same regardless of light/dark theme. Plotly's own
hover tooltip is turned off (`hoverinfo="none"`) — it still fires
`hoverData` on every pixel, but nothing is rendered by Plotly itself. A
clientside callback reads `hoverData`, redoes the hue/saturation-from-pixel
math in JavaScript, and writes the resulting hex straight into a
semi-transparent overlay `Div` stacked on top of the center swatch — a
server round trip on every mouse-move would be unusable:

```python
clientside_callback(
    """
    function(wheelHover, photoHover) {
        // ... same polar hue/saturation math as _hue_sat_from_pixel, in JS
        return [
            Object.assign({}, base, {opacity: 0.55, backgroundColor: hex}),
            hex
        ];
    }
    """,
    Output("picker-demo-preview", "style"),
    Output("picker-demo-hover-hex", "children"),
    Input("picker-demo-wheel", "hoverData"),
    Input("picker-demo-photo", "hoverData"),
)
```

**Photo** looks like the same trick but can't share the wheel's formula: it's
an arbitrary generated raster (a warm-to-cool gradient with a soft glow,
still built with nothing but `colorsys` and `math` — no image file, no new
dependency), and there's no closed-form way to recover a color from its
`(x, y)`. So its `go.Image` trace also ships `customdata` — the real
per-pixel hex, computed once at import — and the hover callback above simply
reads `photoHover.points[0].customdata` instead of doing any math. One
callback, two Inputs, and `dash_clientside.callback_context.triggered_id`
tells it which graph is actually being hovered.

Clicking the wheel or the photo fires `clickData`, which carries the exact
pixel the user clicked — Python re-derives the color (a formula for the
wheel, a table lookup for the photo) and the callback *locks* it into the
swatch underneath the preview overlay. The marker trace that shows where the
last pick landed is moved with `Patch()` instead of rebuilding the whole
figure, so a click ships roughly 40 bytes back to the browser instead of
re-serializing the entire raster:

```python
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
    triggered = ctx.triggered_id
    wheel_figure = photo_figure = no_update
    if triggered == "picker-demo-wheel" and wheel_click:
        point = wheel_click["points"][0]
        hex_color = _hex_from_pixel(point["x"], point["y"])
        wheel_figure = Patch()
        wheel_figure["data"][1]["x"] = [point["x"]]
        wheel_figure["data"][1]["y"] = [point["y"]]
    elif triggered == "picker-demo-photo" and photo_click:
        point = photo_click["points"][0]
        hex_color = _hex_from_photo_pixel(point["x"], point["y"])
        photo_figure = Patch()
        photo_figure["data"][1]["x"] = [point["x"]]
        photo_figure["data"][1]["y"] = [point["y"]]
    elif isinstance(triggered, dict) and triggered.get("type") in (
        "picker-demo-petal", "picker-demo-ring"
    ):
        hex_color = triggered["color"]
    else:
        hex_color = _DEFAULT_COLOR
    ...
```

**Flower** and **Ring** are plain `html.Div`s carrying a pattern-matching id
— `{"type": "picker-demo-petal", "color": <hex>}` or `{"type":
"picker-demo-ring", "color": <hex>}` — positioned with plain arithmetic
(`math.sin`/`math.cos` for the ring, CSS `rotate()` for the petals). The
click callback above listens to all four shapes' click-style inputs at once
and reads `ctx.triggered_id` to know which one fired — no `dcc.Store`
needed anywhere.

They also each carry a `data-picker-color` attribute rather than a hover
prop (`html.Div` has none). A second clientside callback — fired once per
shape switch — binds native `mouseenter`/`mouseleave` listeners to every
`[data-picker-color]` element still on the page and pushes straight into the
same two preview outputs with `window.dash_clientside.set_props`, so hovering
a petal or a ring swatch previews it exactly like hovering the wheel or the
photo.

All four shapes stay mounted in the DOM at all times; a third, smaller
callback just toggles which one is `display: block` based on the
`SegmentedControl`'s value, so switching shapes never destroys or re-creates
a picker's state.

---

### The Standalone App

`color_picker_app.py` is a fully independent, single-file Dash app — its own
`Dash(__name__)` instance, its own `/llms.txt` Flask route, no imports from
this repo's `pages/` or `components/`. Run it on its own with:

```bash
python color_picker_app.py
```

It serves on port 8560, separate from the main site's 8559.

Source code:

.. source::color_picker_app.py
    :defaultExpanded: false
    :withExpandedButton: true
