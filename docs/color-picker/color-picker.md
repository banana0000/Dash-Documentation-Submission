---
name: Color Picker *
description: A color picker with three switchable shapes -- a continuous HSV wheel, clickable petals, and a ring of swatches
endpoint: /examples/color-picker
package: color-picker
icon: mdi:palette-outline
---

.. llms_copy::Color Picker *

.. toc::

### Introduction

One color picker, three shapes. A `dmc.SegmentedControl` filters which shape
is visible — **Wheel** (a continuous HSV wheel you sample by clicking
anywhere on it, like an eyedropper), **Flower** (six clickable preset
petals), or **Ring** (twelve preset swatches arranged in a circle). All
three feed the same center swatch and hex readout.

---

### Live Demo

Switch shapes with the control at the top, then click to pick a color:

.. exec::docs.color-picker.picker
    :code: false
Source code:

.. source::docs/color-picker/picker.py

---

### How It Works

**Wheel** is a `dcc.Graph` showing a static HSV raster (hue by angle,
saturation by radius, value fixed at 1) built once at import time with
`colorsys.hsv_to_rgb`, sitting on an explicit white card (`backgroundColor:
"white"`) so it reads the same regardless of light/dark theme. Each pixel
also carries its hex string as `customdata`, so Plotly's own hover box shows
the exact color under the pointer via a `hovertemplate` — a `dmc.Tooltip`
wrapper was tried here first, but its pointer-tracking overlay intercepted
clicks before they reached the graph, so the hover box stays native to
Plotly instead:

```python
go.Image(
    z=_WHEEL_RGBA,
    customdata=_WHEEL_HEX,
    hovertemplate="%{customdata}<extra></extra>",
)
```

Clicking the wheel fires `clickData`, which carries the exact pixel the
user clicked — that pixel is run back through the same hue/saturation math
to recover the color, and a small ring marker (a `go.Scatter` point) is
drawn at that spot so the pick stays visible:

```python
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
    ...
```

**Flower** and **Ring** are plain `html.Div`s carrying a pattern-matching id
— `{"type": "picker-petal", "color": <hex>}` or `{"type": "picker-ring",
"color": <hex>}` — positioned with plain arithmetic (`math.sin`/`math.cos`
for the ring, CSS `rotate()` for the petals). The same callback above
listens to all three shapes' inputs at once and reads `ctx.triggered_id` to
know which one fired — no `dcc.Store` needed anywhere.

All three shapes stay mounted in the DOM at all times; a second, smaller
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
